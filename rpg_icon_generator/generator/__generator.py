import math
import copy
from rpg_icon_generator.utils.vector import Vector
from rpg_icon_generator.utils.color import Color
from rpg_icon_generator.utils.misc import float_range, floatLerp
from rpg_icon_generator.generator.__drawing import Drawing
from rpg_icon_generator.utils.random import Random
from rpg_icon_generator.utils.bound import Bound
from rpg_icon_generator.utils.constants import RARITY_COLOR, RARITY_RANGE

class Generator(Drawing):
    def set_seed(self, s):
        self.random = Random(s)
    
    def set_drawing_bound(self, dimension, complexity):
        s = self._get_turtle_bound_offset_from_complexity(complexity)
        self.drawing_bound = Bound(0, 0, dimension, dimension)
        self.turtle_bound = Bound(s, s, dimension - 2*s, dimension - 2*s)
        self.dscale = self.turtle_bound.h / 32

    def _get_turtle_bound_offset_from_complexity(self, c):
        out =  math.ceil((0.4 + ((-0.4 / 100) * c)) * self.dimension)
        if out < 5:
            out = 5
        return out
    def _draw_crossguard_helper(self, params):
        # the color of the xguard
        xguardColorLight = Color.hsv2rgb(self.random.randomRange(
            0, 360), self.random.randomFloatLow()*0.5, self.random.randomRangeFloat(0.7, 1))
        # the shadow color of the xguard
        xguardColorDark = xguardColorLight.copy().colorDarken(0.6)
        # the amount of symmetry for the xguard
        xguardSymmetry = 0 if self.random.randomFloat() < 0.3 else 1
        # the thickness of the xguard
        xguardThickness = self.random.randomRangeFloatHigh(1, 2.5)
        # the bottom taper of the xguard
        xguardBottomTaper = self.random.randomFloat()
        # the top taper of the xguard
        xguardTopTaper = floatLerp(self.random.randomFloat(
        ), xguardBottomTaper, self.random.randomFloatExtreme())
        # chance for the xguard to acquire a curve (per pixel)
        xguardOmegaChance = 0.3
        # max magnitude of xguard omega add
        xguardOmegaAmount = math.pi/8
        # maximum absolute xguard omega
        xguardMaxOmega = (xguardThickness-1)**2 * math.pi/7
        # size of each step in sampling the xguard curve
        xguardSampleStepSize = math.sqrt(2)

        # produce xguard shape
        currentPoint = Vector(
            params["positionDiag"], self.drawing_bound.h - params["positionDiag"])
        currentPoint = [currentPoint, Vector(currentPoint)]
        xguardControlPoints = [[], []]
        xguardAngle = [-math.pi * 3/4, math.pi/4]
        xguardOmega = [0, 0]
        for xguardProgress in float_range(0, params["halfLength"], xguardSampleStepSize):
            for side in range(2):
                velocity = Vector(
                    math.cos(xguardAngle[side]), math.sin(xguardAngle[side]))
                newPoint = Vector(currentPoint[side])
                if side == 1:
                    symmetricPoint = Vector(
                        self.drawing_bound.h - currentPoint[0].y,
                        self.drawing_bound.w - currentPoint[0].x)
                    newPoint.lerpTo(symmetricPoint, xguardSymmetry)
                newPoint.widthT = xguardThickness/2
                newPoint.widthB = xguardThickness/2
                newPoint.normal = Vector(
                    velocity.y, -1 * velocity.x).multiplyScalar(side*2-1)
                newPoint.dist = xguardProgress
                xguardControlPoints[side].append(newPoint)
            for side in range(2):
                velocity = Vector(
                    math.cos(xguardAngle[side]), math.sin(xguardAngle[side]))
                if self.random.randomFloat() < xguardOmegaChance:
                    xguardOmega[side] += self.random.randomRangeFloat(
                        -xguardOmegaAmount, xguardOmegaAmount)
                    xguardOmega[side] = math.copysign(
                        1, xguardOmega[side]) * min(xguardMaxOmega, abs(xguardOmega[side]))
                xguardStep = Vector(velocity).multiplyScalar(
                    xguardSampleStepSize)
                currentPoint[side].addVector(xguardStep)
                xguardAngle[side] += xguardOmega[side]

        for side in range(2):
            controlPoints = xguardControlPoints[side]
            for i in range(len(controlPoints)):
                controlPoints[i].addVector(Vector(self.turtle_bound.x, - self.turtle_bound.y))
                # calculate normalized distance
                controlPoints[i].normalizedDist = controlPoints[i].dist / \
                    params["halfLength"]
                # apply taper
                controlPoints[i].widthT *= min(
                    1, (1 - controlPoints[i].normalizedDist) / xguardTopTaper)
                controlPoints[i].widthB *= min(
                    1, (1 - controlPoints[i].normalizedDist) / xguardBottomTaper)

        for x in range(self.turtle_bound.x, self.turtle_bound.w + self.turtle_bound.x):
            for y in range(self.turtle_bound.y, self.turtle_bound.h + self.turtle_bound.y):
                # find the minimum distance to the xguard core
                # OPT: obviously inefficient
                coreDistanceSq = 100000
                bestPoint = None
                for side in range(2):
                    controlPoints = xguardControlPoints[side]
                    for i in range(len(controlPoints)):
                        distanceSq = controlPoints[i].distanceToSq(x, y)
                        if distanceSq < coreDistanceSq:
                            coreDistanceSq = distanceSq
                            bestPoint = controlPoints[i]
                dotProduct = bestPoint.normal.dotProduct(
                    x - bestPoint.x, y - bestPoint.y)
                useWidth = bestPoint.widthB if dotProduct < 0 else bestPoint.widthT
                coreDistance = math.sqrt(coreDistanceSq)
                if coreDistance <= useWidth:
                    distFromTop = bestPoint.widthT + \
                        coreDistance if dotProduct < 0 else bestPoint.widthT - coreDistance
                    darkAmt = distFromTop / \
                        (bestPoint.widthB + bestPoint.widthT)
                    self.draw_pixel(x, y, Color.colorLerp(
                        xguardColorLight, xguardColorDark, darkAmt))
        return {
            "colorLight": xguardColorLight,
            "colorDark": xguardColorDark
        }

    def _draw_grip_helper(self, hiltParams):
        # the radius of the hilt in pixel diagonals
        hiltRadius = 0.5 * \
            math.ceil(self.random.randomRange(0, 2) * self.dscale)
        hiltRadius = hiltRadius + 0.01 if hiltRadius == 0 else hiltRadius
        if hiltParams["maxRadius"] is not None:
            hiltRadius = min(hiltParams["maxRadius"], hiltRadius)

        # wavelength of the hilt texture ( in diagonal pixels)
        hiltWavelength = max(2, math.ceil(
            self.random.randomRange(3, 6) * self.dscale))
        # amplitude of the hilt wave
        hiltWaveAmplitude = math.ceil(
            self.random.randomRange(1, 3) * self.dscale)
        # the color of the hilt
        hiltColorLight = Color.hsv2rgb(self.random.randomRange(
            0, 360), self.random.randomFloat(), self.random.randomRangeFloat(0.7, 1))
        # the color of the hilt inner shadows
        hiltColorDark = hiltColorLight.copy().colorDarken(1)

        # start location of the hilt(diagonal axis, diagonal pixels)
        hiltRadiusOdd = (hiltRadius % 2) != 0

        for l in float_range(0, hiltParams["lengthDiag"], 0.5):
            al = hiltParams["startDiag"] + l
            gripWave = abs(math.cos(math.pi * 2 * l / hiltWavelength))
            color = Color.colorLerp(hiltColorDark, hiltColorLight, gripWave)

            # determine draw parameters
            core = Vector(al + self.turtle_bound.x, self.drawing_bound.h - (al + self.turtle_bound.y))
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
                self.draw_pixel(core.x + h, core.y + h, color.copy().colorDarken(darkenAmt))

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

        bladeOmegaDecay = 0.01
        # radius of the blade at its base
        bladeStartRadius = math.ceil(
            self.random.randomRange(2, 4) * self.dscale)

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
        currentPoint = Vector(
            bladeStartOrtho + self.turtle_bound.x,self.drawing_bound.h - (bladeStartOrtho + self.turtle_bound.y))
        currentDist = 0
        currentWidthL = bladeStartRadius
        currentWidthR = bladeStartRadius + self.random.randomRange(-1, 2)
        velocity = Vector()
        velocityScaled = Vector()
        angle = -math.pi / 4
        omega = 0  # velocity rotation in radians per pixel

        first = True
        while first or self.turtle_bound.contains(currentPoint):
            first = False

            bladeWidthCosine = bladeWidthCosineAmp * \
                math.cos(bladeWidthCosineOffset + currentDist / bladeWidthCosineWavelength)
            useAngle = angle + bladeWiggleAmp * \
                math.sin(math.pi * 2 * currentDist/bladeWiggleWavelength)
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
                omega = math.copysign(1, omega) * \
                    min(bladeMaxOmega, abs(omega))

            velocityScaled.set(velocity).multiplyScalar(bladeSampleStepSize)
            currentPoint.addVector(velocityScaled)
            currentDist += bladeSampleStepSize
            omega *= bladeOmegaDecay
            angle += omega * bladeSampleStepSize

        for pt in bladeCorePoints:
            # calculate normalized distance
            pt.normalizedDist = pt.dist / currentDist
            # apply taper
            invTaperFactor = 1 - taperFactor
            taper = 1 if pt.normalizedDist <= invTaperFactor else (
                1-pt.normalizedDist) / taperFactor
            pt.widthL *= taper
            pt.widthR *= taper

        # forward-axis color of the blade at the tip
        colorBladeLinearTipHsv = {
            "h": self.random.randomRangeFloat(0, 360),
            "s": self.random.randomFloatExtreme() * 0.6 if self.random.randomFloat() < 0.3 else 0,
            "v": self.random.randomRangeFloat(0.75, 1)
        }
        colorBladeLinearTip = Color.hsv2rgb(**colorBladeLinearTipHsv)
        # forward-axis color of the blade at the hilt
        colorBladeLinearHilt = colorBladeLinearTip.copy().colorDarken(0.7).colorRandomize(16, self.random)
        # amount to lighten blade edge
        bladeEdgeLighten = 0.5
        # amount to darken blade far half
        bladeRightDarken = 0.5

        for x in range(self.drawing_bound.w):
            for y in range(self.drawing_bound.h):
                # self.draw_red_pixel(x, y)
                # never draw behind first core point
                dotProduct = bladeCorePoints[0].forward.dotProduct(
                    x - bladeCorePoints[0].x, y - bladeCorePoints[0].y)
                if dotProduct < 0:
                    continue

                # find the minimum distance to the blade core
                coreDistanceNorm = 1000000
                bestPoint = None

                for corePoint in bladeCorePoints:
                    # normalizes distance based on width
                    dotProduct = corePoint.normal.dotProduct(
                        x - corePoint.x, y - corePoint.y)
                    useWidth = corePoint.widthL if dotProduct < 0 else corePoint.widthR
                    distanceNorm = corePoint.distanceTo(x, y) / useWidth
                    if distanceNorm < coreDistanceNorm:
                        coreDistanceNorm = distanceNorm
                        bestPoint = corePoint

                if bestPoint is None:
                    continue

                dotProduct = bestPoint.normal.dotProduct(
                    x - bestPoint.x, y - bestPoint.y)
                useWidth = bestPoint.widthL if dotProduct < 0 else bestPoint.widthR
                coreDistance = bestPoint.distanceTo(x, y)
                if coreDistance <= useWidth or coreDistance <= minimumBladeWidth:
                    color = Color.colorLerp(
                        colorBladeLinearHilt, colorBladeLinearTip, bestPoint.normalizedDist)

                    # do not change core
                    if bestPoint.x == x and bestPoint.y == y:
                        pass
                    else:
                        edgeColor = color.copy().colorLighten(bladeEdgeLighten)
                        darkColor = color.copy().colorDarken(bladeRightDarken)
                        nonEdgeColor = darkColor if dotProduct > 0 else color
                        # lighten edge
                        if useWidth > bladeCoreEdgeExcludeWidth:
                            edgeWidthMin = useWidth - bladeEdgeWidth
                            edgeAmount = (
                                coreDistance - edgeWidthMin) / bladeEdgeWidth
                            edgeAmount = 1 - (1-edgeAmount)*(1-edgeAmount)
                            color = Color.colorLerp(
                                nonEdgeColor, edgeColor, edgeAmount)

                    self.draw_pixel(x, y, color)
        return {
            "startDiag": startDiag,
            "startOrtho": bladeStartOrtho,
            "startRadius": bladeStartRadius
        }

    def _draw_round_ornament_helper(self, params):
        pommelColorLight = params["colorLight"]
        pommelColorDark = params["colorDark"]
        pommelRadius = params["radius"]
        shadowCenter = Vector(0.5, 1).normalize().multiplyScalar(pommelRadius).addVector(params["center"])
        highlightCenter = Vector(-1, -1).normalize().multiplyScalar(pommelRadius * 0.7).addVector(params["center"])
        for x in range(math.ceil(params["center"].x + pommelRadius)):
            for y in range(math.floor(params["center"].y - pommelRadius), math.ceil(params["center"].y + pommelRadius)):
                radius = params["center"].distanceTo(x, y)
                if radius <= pommelRadius:
                    shadowDist = shadowCenter.distanceTo(x, y)
                    highlightDist = highlightCenter.distanceTo(x, y)
                    darkAmt = 1-min(1, 0.8 * shadowDist / pommelRadius)
                    lightAmt = 1-min(1, highlightDist / pommelRadius)
                    self.draw_pixel(x, y, Color.colorLerp(pommelColorLight, pommelColorDark, darkAmt).colorLighten(lightAmt))

    def _draw_border(self):
        width = self.drawing_bound.w
        height = self.drawing_bound.h
        border_pixels = []
        for x in range(width):
            for y in range(height):
                pixel = self.get_pixel_data(x, y)
                # if this pixel is empty or edge
                if pixel.a == 0 or x == 0 or x == width - 1 or y == 0 or y == height - 1:
                    # and any orthogonal pixel isn't
                    nxPix = self.get_pixel_data(x-1, y)
                    nyPix = self.get_pixel_data(x, y-1)
                    pxPix = self.get_pixel_data(x+1, y)
                    pyPix = self.get_pixel_data(x, y+1)
                    if x > 0 and nxPix.a > 0 or x < width - 2 and pxPix.a > 0 or y > 0 and nyPix.a > 0 or y < height - 2 and pyPix.a > 0:
                        border_pixels.append((x, y))
        
        for px, py in border_pixels:
            self.draw_pixel(px, py, Color(0, 0, 0))

    def _get_rarity_from_complexity(self, c):
        for name, cplx in RARITY_RANGE.items():
            if cplx[0] <= c <= cplx[1]:
                return name

    def _get_border_size_from_complexity(self, complexity):
        rSpan = 100
        min_border = 1
        border_span = (self.dimension*0.25) - min_border

        # Convert the left range into a 0-1 range (float)
        valueScaled = float(complexity) / float(rSpan)

        # Convert the 0-1 range into a value in the right range.
        return int(min_border + (valueScaled * border_span))

    def _draw_rarity_border(self, complexity):
        lighten_factor = 0.4
        rarity = self._get_rarity_from_complexity(complexity)
        border_size = self._get_border_size_from_complexity(complexity)
        master_color = Color(**RARITY_COLOR[rarity])
        lighten_color = master_color.copy().colorLighten(lighten_factor)
        colors = [lighten_color]
        for i in range(1, border_size):
            c = master_color.copy().colorLighten(lighten_factor - (i * (lighten_factor/(border_size + 1))))
            c.a -= i * (1/(border_size + 1))
            colors.append(c)
        width = self.drawing_bound.w
        height = self.drawing_bound.h
        for x in range(width):
            for y in range(height):
                for n in range(border_size):
                    pixel = self.get_pixel_data(x, y)
                    if pixel.a == 0 and (x == n or x == width - (1+n) or y == n or y == height - (1+n)):
                        self.draw_pixel(x, y, colors[n])

