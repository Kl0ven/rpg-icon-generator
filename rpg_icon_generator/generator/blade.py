from rpg_icon_generator.utils.vector import Vector
from rpg_icon_generator.utils.bound import Bound
from rpg_icon_generator.utils.random import Random
from rpg_icon_generator.utils.color import hsv2rgb, colorDarken, colorRandomize, colorLerp, colorLighten, float_range, floatLerp
import math
from rpg_icon_generator.generator.__drawing import Drawing


class Blade_Generator(Drawing):
    def generate(self, seed, dimension, output_directory):
        self.reset_canvas(dimension, output_directory)
        self.random = Random(seed)
        self.dimension = dimension
        self.bounds = Bound(0, 0, dimension, dimension)
        self.bounds1 = Bound(1, 1, self.bounds.w - 2, self.bounds.h - 2)
        self.dscale = self.bounds.h / 32

        # length of the pommel
        pommelLength = math.ceil(
            self.random.randomFloatLow() * 2 * self.dscale)
        # length of the hilt
        hiltLength = math.ceil(self.random.randomRange(6, 11) * self.dscale)
        # width of the xguard
        xguardWidth = math.ceil(self.random.randomRange(1, 4) * self.dscale)

        bladeResults = self._draw_blade_helper(pommelLength + hiltLength + xguardWidth)

        # draw the hilt
        hiltStartDiag = math.floor(pommelLength * math.sqrt(2))
        hiltParams = {
            "startDiag": hiltStartDiag,
            "lengthDiag": math.floor(bladeResults["startOrtho"] - hiltStartDiag),
            "maxRadius": bladeResults["startRadius"]
        }
        self._draw_grip_helper(hiltParams)

        # draw the crossguard
        crossguardParams = {
            "positionDiag": bladeResults["startOrtho"],
            "halfLength": bladeResults["startRadius"] * (1 + 2 * self.random.randomFloatLow()) + 1
        }
        crossguardResults = self._draw_crossguard_helper(crossguardParams)

        self.export(seed)

    def _draw_crossguard_helper(self, params):
        # the color of the xguard
        xguardColorLight = hsv2rgb(self.random.randomRange(0, 360), self.random.randomFloatLow()*0.5, self.random.randomRangeFloat(0.7, 1))
        # the shadow color of the xguard
        xguardColorDark = colorDarken(xguardColorLight, 0.6)
        # the amount of symmetry for the xguard
        xguardSymmetry = 0 if self.random.randomFloat() < 0.3 else 1
        # the thickness of the xguard
        xguardThickness = self.random.randomRangeFloatHigh(1, 2.5)
        # the bottom taper of the xguard
        xguardBottomTaper = self.random.randomFloat()
        # the top taper of the xguard
        xguardTopTaper = floatLerp(self.random.randomFloat(), xguardBottomTaper, self.random.randomFloatExtreme())
        # chance for the xguard to acquire a curve (per pixel)
        xguardOmegaChance = 0.3
        # max magnitude of xguard omega add
        xguardOmegaAmount = math.pi/8
        # maximum absolute xguard omega
        xguardMaxOmega = (xguardThickness-1)**2 * math.pi/7
        # size of each step in sampling the xguard curve
        xguardSampleStepSize = math.sqrt(2)

    def _draw_grip_helper(self, hiltParams):
        # the radius of the hilt in pixel diagonals
        hiltRadius = 0.5 * math.ceil(self.random.randomRange(0, 2) * self.dscale)
        hiltRadius = hiltRadius + 0.01 if hiltRadius == 0 else hiltRadius 
        if hiltParams["maxRadius"] is not None:
            hiltRadius = min(hiltParams["maxRadius"], hiltRadius)

        # wavelength of the hilt texture ( in diagonal pixels)
        hiltWavelength = max(2, math.ceil(self.random.randomRange(3, 6) * self.dscale))
        # amplitude of the hilt wave
        hiltWaveAmplitude = math.ceil(self.random.randomRange(1, 3) * self.dscale)
        # the color of the hilt
        hiltColorLight = hsv2rgb(self.random.randomRange(0, 360), self.random.randomFloat(), self.random.randomRangeFloat(0.7, 1))
        # the color of the hilt inner shadows
        hiltColorDark = colorDarken(hiltColorLight, 1)

        # start location of the hilt(diagonal axis, diagonal pixels)
        hiltRadiusOdd = (hiltRadius % 2) != 0

        for l in float_range(0, hiltParams["lengthDiag"], 0.5):
            al = hiltParams["startDiag"] + l
            gripWave = abs(math.cos(math.pi * 2 * l / hiltWavelength))
            color = colorLerp(hiltColorDark, hiltColorLight, gripWave)

            # determine draw parameters
            core = Vector(al, self.bounds.h - 1 - al)
            isOdd = (al % 1) != 0
            core.x = math.ceil(core.x)
            core.y = math.ceil(core.y)
            if isOdd:
                left = -math.ceil(hiltRadius)
                right = math.floor(hiltRadius)
                if not hiltRadiusOdd:
                    right -= 1
            else:
                left = -math.floor(hiltRadius)
                right = math.floor(hiltRadius)

            # draw grip line
            for h in range(left, right+1):
                darkenAmt = max(0, h + hiltRadius) / (hiltRadius*4)
                self.draw_pixel(core.x + h, core.y + h, colorDarken(color, darkenAmt))


    def _draw_blade_helper(self, startDiag):
        # determines the angle of the taper of the blade tip(as a ratio of the blade length)
        taperFactor = self.random.randomFloatLow()
        # minimum blade width
        minimumBladeWidth = 1
        # size of each step in sampling the blade curve
        bladeSampleStepSize = math.sqrt(2)
        # width of the lighter edge pixels
        bladeEdgeWidth = 1
        # minimum width of the blade core before edge can be drawn
        bladeCoreEdgeExcludeWidth = 1
        # chance of the blade aquiring a random jog(per pixel)
        bladeJogChance = 0.04
        # chance to jog is reduced during the first this many pixels
        bladeJogChanceLeadIn = math.ceil(12 * self.dscale)
        # max magnitude of a blade jog
        bladeJogAmount = math.pi / 4
        # chance of the blade acquiring a curve(per pixel)
        bladeOmegaChance = 0.02
        # max magnitude of blade omega add
        bladeOmegaAmount = math.pi / 32
        # maximum absolute omega
        bladeMaxOmega = math.pi / 32
        # radius of the blade at its base
        bladeStartRadius = math.ceil(self.random.randomRange(2, 4) * self.dscale)

        # amplitude of the cosine wave applied to blade width
        bladeWidthCosineAmp = math.ceil(
            max(0, self.random.randomFloatLow()*1.2-0.2) * 2 * self.dscale)
        # wavelength of the cosine wave applied to blade width
        bladeWidthCosineWavelength = math.ceil(self.random.randomRange(
            3 * max(1, bladeWidthCosineAmp-1), 12) * self.dscale)
        # offset of the cosine wave applied to blade width
        bladeWidthCosineOffset = self.random.randomRangeFloat(0, math.pi * 2)

        # amplitude of the blade core wiggle curve
        bladeWiggleAmp = max(0, self.random.randomFloat()
                             * 8-7) * math.pi/4 * self.dscale
        # wavelength of the blade core wiggle curve
        bladeWiggleWavelength = math.ceil(
            self.random.randomRangeFloat(6, 18) * self.dscale)

        # produce blade shape
        bladeCorePoints = []
        bladeStartOrtho = math.floor(startDiag / math.sqrt(2))
        currentPoint = Vector(bladeStartOrtho, self.bounds.h - 1 - bladeStartOrtho)
        currentDist = 0
        currentWidthL = bladeStartRadius
        currentWidthR = bladeStartRadius + self.random.randomRange(-1, 2)
        velocity = Vector()
        velocityScaled = Vector()
        angle = -math.pi / 4
        omega = 0 # velocity rotation in radians per pixel

        first = True
        while first or self.bounds1.contains(currentPoint):
            first = False

            bladeWidthCosine = bladeWidthCosineAmp * math.cos(bladeWidthCosineOffset + currentDist / bladeWidthCosineWavelength)
            useAngle = angle + bladeWiggleAmp * math.sin(math.pi * 2 * currentDist/bladeWiggleWavelength)
            velocity.set(math.cos(useAngle), math.sin(useAngle))

            newPoint = Vector(currentPoint)
            newPoint.widthL = max(1, currentWidthL + bladeWidthCosine)
            newPoint.widthR = max(1, currentWidthR + bladeWidthCosine)
            newPoint.normal = Vector(-1 * velocity.y, velocity.x).normalize()
            newPoint.forward = Vector(velocity).normalize()
            newPoint.dist = currentDist
            bladeCorePoints.append(newPoint)

            if self.random.randomFloat() <= bladeJogChance * min(1, currentDist/bladeJogChanceLeadIn):
                angle += self.random.randomRangeFloat(-bladeJogAmount, bladeJogAmount)

            if self.random.randomFloat() <= bladeOmegaChance:
                omega += self.random.randomRangeFloat(-bladeOmegaAmount, bladeOmegaAmount)
                omega = math.copysign(1, omega) * min(bladeMaxOmega, abs(omega))

            velocityScaled.set(velocity).multiplyScalar(bladeSampleStepSize)
            currentPoint.addVector(velocityScaled)
            currentDist += bladeSampleStepSize
            angle += omega * bladeSampleStepSize
        
        for pt in bladeCorePoints:
            # calculate normalized distance
            pt.normalizedDist = pt.dist / currentDist
            # apply taper
            invTaperFactor = 1 - taperFactor
            taper = 1 if pt.normalizedDist <= invTaperFactor else (1-pt.normalizedDist) / taperFactor
            pt.widthL *= taper
            pt.widthR *= taper

        # forward-axis color of the blade at the tip
        colorBladeLinearTipHsv = {
            "h": self.random.randomRangeFloat(0, 360),
            "s": self.random.randomFloatExtreme() * 0.6 if self.random.randomFloat() < 0.3 else 0,
            "v": self.random.randomRangeFloat(0.75, 1)
        }
        colorBladeLinearTip = hsv2rgb(**colorBladeLinearTipHsv)
        # forward-axis color of the blade at the hilt
        colorBladeLinearHilt = colorRandomize(colorDarken(colorBladeLinearTip, 0.7), 16, self.random)
        # amount to lighten blade edge
        bladeEdgeLighten = 0.5
        # amount to darken blade far half
        bladeRightDarken = 0.5

        for x in range(self.bounds.w):
            for y in range(self.bounds.h):
                # never draw behind first core point
                dotProduct = bladeCorePoints[0].forward.dotProduct(x - bladeCorePoints[0].x, y - bladeCorePoints[0].y)
                if dotProduct < 0:
                    continue
            
                # find the minimum distance to the blade core
                coreDistanceNorm = 1000000
                bestPoint = None

                for corePoint in bladeCorePoints:
                    # normalizes distance based on width
                    dotProduct = corePoint.normal.dotProduct(x - corePoint.x, y - corePoint.y)
                    useWidth = corePoint.widthL if dotProduct < 0 else corePoint.widthR
                    distanceNorm = corePoint.distanceTo(x, y) / useWidth
                    if distanceNorm < coreDistanceNorm:
                        coreDistanceNorm = distanceNorm
                        bestPoint = corePoint

                if bestPoint is None:
                    continue

                dotProduct = bestPoint.normal.dotProduct(x - bestPoint.x, y - bestPoint.y)
                useWidth = bestPoint.widthL if dotProduct < 0 else bestPoint.widthR
                coreDistance = bestPoint.distanceTo(x, y)
                if coreDistance <= useWidth or coreDistance <= minimumBladeWidth:
                    color = colorLerp(colorBladeLinearHilt, colorBladeLinearTip, bestPoint.normalizedDist)

                    # do not change core
                    if bestPoint.x == x and bestPoint.y == y:
                        pass
                    else:
                        edgeColor = colorLighten(color, bladeEdgeLighten)
                        darkColor = colorDarken(color, bladeRightDarken)
                        nonEdgeColor = darkColor if dotProduct > 0 else color
                        # lighten edge
                        if useWidth > bladeCoreEdgeExcludeWidth:
                            edgeWidthMin = useWidth - bladeEdgeWidth
                            edgeAmount = (coreDistance - edgeWidthMin) / bladeEdgeWidth
                            edgeAmount = 1 - (1-edgeAmount)*(1-edgeAmount)
                            color = colorLerp(nonEdgeColor, edgeColor, edgeAmount)

                    self.draw_pixel(x, y, color)
        return {
            "startDiag": startDiag,
            "startOrtho": bladeStartOrtho,
            "startRadius": bladeStartRadius
        }



