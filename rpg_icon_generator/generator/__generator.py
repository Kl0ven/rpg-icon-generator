import math
import copy
from rpg_icon_generator.utils.vector import Vector
from rpg_icon_generator.utils.color import Color
from rpg_icon_generator.utils.misc import float_range, float_lerp
from rpg_icon_generator.generator.__drawing import Drawing
from rpg_icon_generator.utils.random import Random
from rpg_icon_generator.utils.bound import Bound
from rpg_icon_generator.utils.constants import RARITY_COLOR, RARITY_RANGE, RARITY_COLOR_SECONDARY
from rpg_icon_generator.generator.__pattern_generator import Pattern_Generator
from shapely.geometry.polygon import Polygon
from shapely.geometry import Point

class Generator(Drawing):
    def set_seed(self, s):
        self.random = Random(s)
    
    def set_drawing_bound(self, dimension, complexity):
        s = self._get_turtle_bound_offset_from_complexity(complexity)
        self.center = self.dimension/2
        self.drawing_bound = Bound(0, 0, dimension, dimension)
        self.turtle_bound = Bound(s, s, dimension - 2*s, dimension - 2*s)
        self.dscale = self.turtle_bound.h / 32

    def _get_turtle_bound_offset_from_complexity(self, c):
        out =  math.ceil((0.4 + ((-0.4 / 100) * c)) * self.dimension)
        if out < 7:
            out = 7
        return out
    def _draw_crossguard_helper(self, params):
        # the color of the xguard
        xguardColorLight = Color.hsv2rgb(self.random.range(
            0, 360), self.random.float_low()*0.5, self.random.range_float(0.7, 1))
        # the shadow color of the xguard
        xguardColorDark = xguardColorLight.copy().darken(0.6)
        # the amount of symmetry for the xguard
        xguardSymmetry = 0 if self.random.float() < 0.3 else 1
        # the thickness of the xguard
        xguardThickness = self.random.range_float_high(1, 2.5)
        # the bottom taper of the xguard
        xguardBottomTaper = self.random.float()
        # the top taper of the xguard
        xguardTopTaper = float_lerp(self.random.float(
        ), xguardBottomTaper, self.random.float_extreme())
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
                    newPoint.lerp_to(symmetricPoint, xguardSymmetry)
                newPoint.widthT = xguardThickness/2
                newPoint.widthB = xguardThickness/2
                newPoint.normal = Vector(
                    velocity.y, -1 * velocity.x).multiply_scalar(side*2-1)
                newPoint.dist = xguardProgress
                xguardControlPoints[side].append(newPoint)
            for side in range(2):
                velocity = Vector(
                    math.cos(xguardAngle[side]), math.sin(xguardAngle[side]))
                if self.random.float() < xguardOmegaChance:
                    xguardOmega[side] += self.random.range_float(
                        -xguardOmegaAmount, xguardOmegaAmount)
                    xguardOmega[side] = math.copysign(
                        1, xguardOmega[side]) * min(xguardMaxOmega, abs(xguardOmega[side]))
                xguardStep = Vector(velocity).multiply_scalar(
                    xguardSampleStepSize)
                currentPoint[side].add_vector(xguardStep)
                xguardAngle[side] += xguardOmega[side]

        for side in range(2):
            controlPoints = xguardControlPoints[side]
            for i in range(len(controlPoints)):
                controlPoints[i].add_vector(Vector(self.turtle_bound.x, - self.turtle_bound.y))
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
                        distanceSq = controlPoints[i].distance_to_sq(x, y)
                        if distanceSq < coreDistanceSq:
                            coreDistanceSq = distanceSq
                            bestPoint = controlPoints[i]
                dot_product = bestPoint.normal.dot_product(
                    x - bestPoint.x, y - bestPoint.y)
                useWidth = bestPoint.widthB if dot_product < 0 else bestPoint.widthT
                coreDistance = math.sqrt(coreDistanceSq)
                if coreDistance <= useWidth:
                    distFromTop = bestPoint.widthT + \
                        coreDistance if dot_product < 0 else bestPoint.widthT - coreDistance
                    darkAmt = distFromTop / \
                        (bestPoint.widthB + bestPoint.widthT)
                    self.draw_pixel(x, y, Color.lerp(
                        xguardColorLight, xguardColorDark, darkAmt))
        return {
            "colorLight": xguardColorLight,
            "colorDark": xguardColorDark
        }

    def _draw_grip_helper(self, hiltParams):
        # the radius of the hilt in pixel diagonals
        hiltRadius = 0.5 * \
            math.ceil(self.random.range(0, 2) * self.dscale)
        hiltRadius = hiltRadius + 0.01 if hiltRadius == 0 else hiltRadius
        if hiltParams["maxRadius"] is not None:
            hiltRadius = min(hiltParams["maxRadius"], hiltRadius)

        # wavelength of the hilt texture ( in diagonal pixels)
        hiltWavelength = max(2, math.ceil(
            self.random.range(3, 6) * self.dscale))
        # the color of the hilt
        hiltColorLight = Color.hsv2rgb(self.random.range(
            0, 360), self.random.float(), self.random.range_float(0.7, 1))
        # the color of the hilt inner shadows
        hiltColorDark = hiltColorLight.copy().darken(1)

        # start location of the hilt(diagonal axis, diagonal pixels)
        hiltRadiusOdd = (hiltRadius % 2) != 0

        for l in float_range(0, hiltParams["lengthDiag"], 0.5):
            al = hiltParams["startDiag"] + l
            gripWave = abs(math.cos(math.pi * 2 * l / hiltWavelength))
            color = Color.lerp(hiltColorDark, hiltColorLight, gripWave)

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
                self.draw_pixel(core.x + h, core.y + h, color.copy().darken(darkenAmt))
        return hiltRadius

    def _draw_blade_helper(self, startDiag):
        # determines the angle of the taper of the blade tip(as a ratio of the blade length)
        taperFactor = self.random.float_low()
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
            self.random.range(2, 4) * self.dscale)

        # amplitude of the cosine wave applied to blade width
        bladeWidthCosineAmp = math.ceil(
            max(0, self.random.float_low()*1.2-0.2) * 2 * self.dscale)
        # wavelength of the cosine wave applied to blade width
        bladeWidthCosineWavelength = math.ceil(self.random.range(
            3 * max(1, bladeWidthCosineAmp-1), 12) * self.dscale)
        # offset of the cosine wave applied to blade width
        bladeWidthCosineOffset = self.random.range_float(0, math.pi * 2)

        # amplitude of the blade core wiggle curve
        bladeWiggleAmp = max(0, self.random.float()
                             * 8-7) * math.pi/4 * self.dscale
        # wavelength of the blade core wiggle curve
        bladeWiggleWavelength = math.ceil(
            self.random.range_float(6, 18) * self.dscale)

        # produce blade shape
        bladeCorePoints = []
        bladeStartOrtho = math.floor(startDiag / math.sqrt(2))
        currentPoint = Vector(
            bladeStartOrtho + self.turtle_bound.x,self.drawing_bound.h - (bladeStartOrtho + self.turtle_bound.y))
        currentDist = 0
        currentWidthL = bladeStartRadius
        currentWidthR = bladeStartRadius + self.random.range(-1, 2)
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

            if self.random.float() <= bladeJogChance * min(1, currentDist/bladeJogChanceLeadIn):
                angle += self.random.range_float(-bladeJogAmount, bladeJogAmount)

            if self.random.float() <= bladeOmegaChance:
                omega += self.random.range_float(-bladeOmegaAmount, bladeOmegaAmount)
                omega = math.copysign(1, omega) * \
                    min(bladeMaxOmega, abs(omega))

            velocityScaled.set(velocity).multiply_scalar(bladeSampleStepSize)
            currentPoint.add_vector(velocityScaled)
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
            "h": self.random.range_float(0, 360),
            "s": self.random.float_extreme() * 0.6 if self.random.float() < 0.3 else 0,
            "v": self.random.range_float(0.75, 1)
        }
        colorBladeLinearTip = Color.hsv2rgb(**colorBladeLinearTipHsv)
        # forward-axis color of the blade at the hilt
        colorBladeLinearHilt = colorBladeLinearTip.copy().darken(0.7).randomize(16, self.random)
        # amount to lighten blade edge
        bladeEdgeLighten = 0.5
        # amount to darken blade far half
        bladeRightDarken = 0.5

        for x in range(self.drawing_bound.w):
            for y in range(self.drawing_bound.h):
                # self.draw_red_pixel(x, y)
                # never draw behind first core point
                dot_product = bladeCorePoints[0].forward.dot_product(
                    x - bladeCorePoints[0].x, y - bladeCorePoints[0].y)
                if dot_product < 0:
                    continue

                # find the minimum distance to the blade core
                coreDistanceNorm = 1000000
                bestPoint = None

                for corePoint in bladeCorePoints:
                    # normalizes distance based on width
                    dot_product = corePoint.normal.dot_product(
                        x - corePoint.x, y - corePoint.y)
                    useWidth = corePoint.widthL if dot_product < 0 else corePoint.widthR
                    distanceNorm = corePoint.distance_to(x, y) / useWidth
                    if distanceNorm < coreDistanceNorm:
                        coreDistanceNorm = distanceNorm
                        bestPoint = corePoint

                if bestPoint is None:
                    continue

                dot_product = bestPoint.normal.dot_product(
                    x - bestPoint.x, y - bestPoint.y)
                useWidth = bestPoint.widthL if dot_product < 0 else bestPoint.widthR
                coreDistance = bestPoint.distance_to(x, y)
                if coreDistance <= useWidth or coreDistance <= minimumBladeWidth:
                    color = Color.lerp(
                        colorBladeLinearHilt, colorBladeLinearTip, bestPoint.normalizedDist)

                    # do not change core
                    if bestPoint.x == x and bestPoint.y == y:
                        pass
                    else:
                        edgeColor = color.copy().lighten(bladeEdgeLighten)
                        darkColor = color.copy().darken(bladeRightDarken)
                        nonEdgeColor = darkColor if dot_product > 0 else color
                        # lighten edge
                        if useWidth > bladeCoreEdgeExcludeWidth:
                            edgeWidthMin = useWidth - bladeEdgeWidth
                            edgeAmount = (
                                coreDistance - edgeWidthMin) / bladeEdgeWidth
                            edgeAmount = 1 - (1-edgeAmount)*(1-edgeAmount)
                            color = Color.lerp(
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
        shadowCenter = Vector(0.5, 1).normalize().multiply_scalar(pommelRadius).add_vector(params["center"])
        highlightCenter = Vector(-1, -1).normalize().multiply_scalar(pommelRadius * 0.7).add_vector(params["center"])
        for x in range(math.ceil(params["center"].x + pommelRadius)):
            for y in range(math.floor(params["center"].y - pommelRadius), math.ceil(params["center"].y + pommelRadius)):
                radius = params["center"].distance_to(x, y)
                if radius <= pommelRadius:
                    shadowDist = shadowCenter.distance_to(x, y)
                    highlightDist = highlightCenter.distance_to(x, y)
                    darkAmt = 1-min(1, 0.8 * shadowDist / pommelRadius)
                    lightAmt = 1-min(1, highlightDist / pommelRadius)
                    self.draw_pixel(x, y, Color.lerp(pommelColorLight, pommelColorDark, darkAmt).lighten(lightAmt))

    def _draw_border(self):
        width = self.drawing_bound.w
        height = self.drawing_bound.h
        border_pixels = []
        for x in range(width):
            for y in range(height):
                pixel = self.get_pixel_data(x, y)
                # if this pixel is empty or edge
                if pixel.a == 0 or x == 0 or x == width - 1 or y == 0 or y == height - 1 or pixel.is_black():
                    # and any orthogonal pixel isn't
                    nxPix = self.get_pixel_data(x-1, y)
                    nyPix = self.get_pixel_data(x, y-1)
                    pxPix = self.get_pixel_data(x+1, y)
                    pyPix = self.get_pixel_data(x, y+1)
                    if x > 0 and not nxPix.is_empty(True) or x < width - 2 and not pxPix.is_empty(True) or y > 0 and not nyPix.is_empty(True) or y < height - 2 and not pyPix.is_empty(True):
                        border_pixels.append((x, y))
        
        for px, py in border_pixels:
            self.draw_pixel(px, py, Color(0, 0, 0))

    def _get_rarity_from_complexity(self, c):
        for name, cplx in RARITY_RANGE.items():
            if cplx[0] <= c <= cplx[1]:
                return name

    def _draw_rarity_border(self, complexity):
        border_size = 3
        lighten_factor = 0.6
        rarity = self._get_rarity_from_complexity(complexity)
        master_color = Color(**RARITY_COLOR[rarity])
        secondary_color = Color(**RARITY_COLOR_SECONDARY[rarity])
        lighten_color = master_color.copy()
        colors = [lighten_color]
        for i in range(1, border_size):
            c = master_color.copy().lighten(i * (lighten_factor/(border_size + 1)))
            colors.append(c)
        width = self.drawing_bound.w
        height = self.drawing_bound.h
        for x in range(width):
            for y in range(height):
                for n in range(border_size):
                    pixel = self.get_pixel_data(x, y)
                    if pixel.a == 0 and (x == n or x == width - (1+n) or y == n or y == height - (1+n)):
                        self.draw_pixel(x, y, colors[n])
        
        self._draw_corner(colors, secondary_color, Vector(border_size, border_size), Vector(1, 1))
        self._draw_corner(colors, secondary_color, Vector(self.drawing_bound.w - 1 - border_size, border_size), Vector(-1, 1))
        self._draw_corner(colors, secondary_color, Vector(border_size, self.drawing_bound.h -1  - border_size), Vector(1, -1))
        self._draw_corner(colors, secondary_color, Vector(self.drawing_bound.w - 1 - border_size, self.drawing_bound.h - 1 - border_size), Vector(-1, -1))

    def _draw_corner(self, colors, secondary_color, pos, mult):
        for x in range(3):
            self.draw_pixel_safe(pos.x + (x*mult.x), pos.y, colors[-2])
        for y in range(3):
            self.draw_pixel_safe(pos.x, pos.y + (y*mult.y), colors[-2])
        for x in range(4):
            self.draw_pixel_safe(pos.x + (x*mult.x), pos.y + (3*mult.y), colors[-1])
        for y in range(4):
            self.draw_pixel_safe(pos.x + (3*mult.x), pos.y + (y*mult.y), colors[-1])

        if mult.x == 1 and mult.y == 1:
            offset = Vector(1, 2)
        elif mult.x == -1 and mult.y == 1:
            offset = Vector(-2, 2)
        elif mult.x == 1 and mult.y == -1:
            offset = Vector(1, -1)
        elif mult.x == -1 and mult.y == -1:
            offset = Vector(-2, -1)

        self.draw_pixel_safe(pos.x + offset.x, pos.y + offset.y, secondary_color)
        self.draw_pixel_safe(pos.x + offset.x, pos.y + offset.y - 1 , secondary_color)
        self.draw_pixel_safe(pos.x + offset.x + 1 , pos.y + offset.y, secondary_color)
        self.draw_pixel_safe(pos.x + offset.x + 1, pos.y + offset.y- 1, Color(255, 255, 255))

        c = colors[-1].copy().lighten(0.2)
        for x in range(4, int(self.center)):
            self.draw_pixel_safe(pos.x + (x*mult.x), pos.y, c)
        for y in range(4, int(self.center)):
            self.draw_pixel_safe(pos.x, pos.y + (y*mult.y), c)

        self.draw_pixel_safe(pos.x + (4*mult.x), pos.y + (1*mult.y), c)
        self.draw_pixel_safe(pos.x + (1*mult.x), pos.y + (4*mult.y), c)


    def _draw_axe_blade_helper(self, origine, offset, body_width=5, body_heigth=10, axe_width=15):
        # the color of the axe
        colorAxeLinearTipHsv = Color.hsv2rgb(
            self.random.range_float(0, 360),
            self.random.float_extreme() * 0.6 if self.random.float() < 0.3 else 0,
            self.random.range_float(0.75, 1)
        )
        axeColorLight = colorAxeLinearTipHsv.copy().lighten(0.5)
        # the shadow color of the axe
        axeColorDark = colorAxeLinearTipHsv.copy().darken(0.5)
        # the amount of symmetry for the axe
        axeSymmetry = 0 if self.random.float() < 0.3 else 1

        # the amount of symmetry for the axe on second axis
        axeSymmetry2 = 0 if self.random.float() < 0.2 else 1
        # the thickness of the axe
        axeThickness = self.random.range_float_high(1, 2.5)
        # chance for the axe to acquire a curve (per pixel)
        axeOmegaChance = 0.6
        # max magnitude of axe omega add
        axeOmegaAmount = math.pi/8
        # maximum absolute axe omega
        axeMaxOmega = ((axeThickness-1)**2 * math.pi/7)*0.2
        # size of each step in sampling the axe curve
        axeSampleStepSize = math.sqrt(2)
        

        angle_45 = math.cos(math.pi/4)

        # self.draw_red_pixel(origine.x, origine.y, 1)
        # produce axe shape
        currentPoint = Vector(self.center, self.center).add_vector(
            Vector(
                angle_45 * offset,
                angle_45 * offset)
        )
        currentPoint = [currentPoint, Vector(currentPoint)]
        axeControlPoints = [[], []]
        axeAngle = [math.pi * 3/4, -math.pi/4]
        axeOmega = [0.08, -0.08]
        for axeProgress in float_range(0, axe_width, axeSampleStepSize):
            for side in range(2):
                velocity = Vector(math.cos(axeAngle[side]), math.sin(axeAngle[side]))
                newPoint = Vector(currentPoint[side])
                if side == 1:
                    symmetricPoint = Vector(
                        currentPoint[0].y,
                        currentPoint[0].x)
                    newPoint.lerp_to(symmetricPoint, axeSymmetry)
                newPoint.widthT = axeThickness/2
                newPoint.widthB = axeThickness/2
                newPoint.normal = Vector(velocity.y, -1 * velocity.x).multiply_scalar(side*2-1)
                newPoint.dist = axeProgress
                axeControlPoints[side].append(newPoint)
            for side in range(2):
                velocity = Vector(math.cos(axeAngle[side]), math.sin(axeAngle[side]))
                if self.random.float() < axeOmegaChance:
                    axeOmega[side] += self.random.range_float(-axeOmegaAmount, axeOmegaAmount)
                    axeOmega[side] = math.copysign(1, axeOmega[side]) * min(axeMaxOmega, abs(axeOmega[side]))
                axeStep = Vector(velocity).multiply_scalar(axeSampleStepSize)
                currentPoint[side].add_vector(axeStep)
                axeAngle[side] += axeOmega[side]

        for side in range(2):
            controlPoints = axeControlPoints[side]
            for i in range(len(controlPoints)):
                controlPoints[i].add_vector(Vector(
                    origine.x - self.center,
                    origine.y - self.center))


        # compute polygone
        poly_node = []
        mid_low = Vector(-angle_45 * body_heigth/2, angle_45 * body_heigth/2)
        poly_node.append(origine.copy().add_vector(mid_low.copy().add_vector(Vector(-angle_45 * body_width/2, -angle_45 * body_width/2))))
        poly_node.append(origine.copy().add_vector(mid_low.copy().add_vector(Vector(angle_45 * body_width/2, angle_45 * body_width/2))))

        poly_node += axeControlPoints[0][::-1]
        poly_node += axeControlPoints[1]


        mid_high = Vector(angle_45 * body_heigth/2, -angle_45 * body_heigth/2)
        poly_node.append(origine.copy().add_vector(mid_high.copy().add_vector(Vector(angle_45 * body_width/2, angle_45 * body_width/2))))
        poly_node.append(origine.copy().add_vector(mid_high.copy().add_vector(Vector(-angle_45 * body_width/2, -angle_45 * body_width/2))))

        if axeSymmetry2:
            s1 = [Vector(self.drawing_bound.h - l.y, self.drawing_bound.w - l.x) for l in axeControlPoints[1][::-1]]
            poly_node += s1
            s2 = [Vector(self.drawing_bound.h - l.y, self.drawing_bound.w - l.x) for l in axeControlPoints[0]]
            poly_node += s2
            axeControlPoints.append(s1)
            axeControlPoints.append(s2)

        poly = Polygon([p.to_coord() for p in poly_node])

        # for i, p in enumerate(poly_node):
        #     c = Color.hsv2rgb(int((i/len(poly_node))*360), 1, 1)
        #     self.draw_pixel(p.x, p.y, c)

        for x in range(self.drawing_bound.w):
            for y in range(self.drawing_bound.h):
                # find the minimum distance to the axe core
                # OPT: obviously inefficient
                coreDistanceSq = 100000
                bestPoint = None
                for controlPoints in axeControlPoints:
                    for i in range(len(controlPoints)):
                        distanceSq = controlPoints[i].distance_to_sq(x, y)
                        if distanceSq < coreDistanceSq:
                            coreDistanceSq = distanceSq
                            bestPoint = controlPoints[i]
                coreDistance = math.sqrt(coreDistanceSq)
                pt = Point(x, y)
                if poly.contains(pt):
                    darkAmt = self.translate(coreDistance, 0, 5, 0, 1)
                    self.draw_pixel(x, y, Color.lerp(axeColorLight, axeColorDark, darkAmt))
        return (axeColorLight, axeColorDark)

    def translate(self, value, leftMin, leftMax, rightMin, rightMax):
        # Figure out how 'wide' each range is
        leftSpan = leftMax - leftMin
        rightSpan = rightMax - rightMin
        # Convert the left range into a 0-1 range (float)
        valueScaled = float(value - leftMin) / float(leftSpan)
        # Convert the 0-1 range into a value in the right range.
        return rightMin + (valueScaled * rightSpan)


    def _draw_hammer_helper(self, origine, body_width=5, body_heigth=10):
        # the color of the axe
        color_hammer_linear_tip_HSV = Color.hsv2rgb(
            self.random.range_float(0, 360),
            self.random.float_extreme() * 0.6 if self.random.float() < 0.3 else 0,
            self.random.range_float(0.75, 1)
        )
        hammer_color_light = color_hammer_linear_tip_HSV.copy().lighten(0.5)
        # the shadow color of the axe
        hammer_color_dark = color_hammer_linear_tip_HSV.copy().darken(0.5)

        hammer_face_offset = Vector(self.random.range(0, 5), self.random.range(3, 5)) 
        angle_45 = math.cos(math.pi/4)


        # cube
        cube_node = []
        mid_low = Vector(-angle_45 * body_heigth/2, angle_45 * body_heigth/2)
        cube_node.append(origine.copy().add_vector(mid_low.copy().add_vector(Vector(-angle_45 * body_width/2, -angle_45 * body_width/2))))
        cube_node.append(origine.copy().add_vector(mid_low.copy().add_vector(Vector(angle_45 * body_width/2, angle_45 * body_width/2))))
        mid_high = Vector(angle_45 * body_heigth/2, -angle_45 * body_heigth/2)
        cube_node.append(origine.copy().add_vector(mid_high.copy().add_vector(Vector(angle_45 * body_width/2, angle_45 * body_width/2))))
        cube_node.append(origine.copy().add_vector(mid_high.copy().add_vector(Vector(-angle_45 * body_width/2, -angle_45 * body_width/2))))
        self._draw_poly(cube_node, hammer_color_dark)

        # bottom face
        bottom_poly = []
        pt = origine.copy().add_vector(mid_low.copy().add_vector(Vector(angle_45 * body_width/2, angle_45 * body_width/2)))
        bottom_poly.append(pt)
        bottom_poly.append(pt.copy().add_vector(hammer_face_offset.copy().rotate(math.pi/4)))
        pt = origine.copy().add_vector(mid_high.copy().add_vector(Vector(angle_45 * body_width/2, angle_45 * body_width/2)))
        bottom_poly.append(pt.copy().add_vector(Vector(hammer_face_offset.y, hammer_face_offset.x).rotate(-math.pi/4)))
        bottom_poly.append(pt)
        self._draw_poly(bottom_poly, hammer_color_light)

        # top face
        top_poly = []
        pt = origine.copy().add_vector(mid_low.copy().add_vector(Vector(-angle_45 * body_width/2, -angle_45 * body_width/2)))
        top_poly.append(pt)
        top_poly.append(pt.copy().add_vector(Vector(hammer_face_offset.x, -1 * hammer_face_offset.y).rotate(math.pi/4)))
        pt = origine.copy().add_vector(mid_high.copy().add_vector(Vector(-angle_45 * body_width/2, -angle_45 * body_width/2)))
        top_poly.append(pt.copy().add_vector(Vector(-1 * hammer_face_offset.y, hammer_face_offset.x).rotate(-math.pi/4)))
        top_poly.append(pt)
        # self.debug_poly(top_poly)
        self._draw_poly(top_poly, hammer_color_light)

        self._draw_pattern_helper(cube_node[0].copy().round(), hammer_color_dark)
        return (hammer_color_light, hammer_color_dark)

    def _draw_pattern_helper(self, start, color):
        cursor = start.copy()
        move = Vector(1, -1)
        move_down = Vector(0, 1)
        dark_color = color.copy().darken(0.5)

        w = self.__get_width(start.copy(), color.copy())
        p = Pattern_Generator(w, self.random)
        x = 0
        y = 0

        while True:
            if self.get_pixel_data(cursor.x, cursor.y) == color:
                if p.nodes[x].value:
                    self.draw_pixel(cursor.x, cursor.y, dark_color)
            cursor.add_vector(move)
            x += 1
            if self.get_pixel_data(cursor.x, cursor.y) != color:
                # out of the box
                cursor = start.add_vector(move_down).copy()
                pixel = self.get_pixel_data(cursor.x, cursor.y)
                while pixel != color:
                    cursor.add_vector(move)
                    pixel = self.get_pixel_data(cursor.x, cursor.y)
                    if pixel is None:
                        return
                p.step()
                y += 1
                x = 0
    
    def __get_width(self, start, color):
        move = Vector(1, -1)
        move_down = Vector(1, 1)
        cursor = start.copy()
        w = 0
        old_w = -1
        while True:
            w += 1
            cursor.add_vector(move)
            if self.get_pixel_data(cursor.x, cursor.y) != color:
                cursor = start.add_vector(move_down).copy()
                j = 0
                while self.get_pixel_data(cursor.x, cursor.y) != color:
                    cursor.add_vector(move)
                    j += 1
                    if j > 20:
                        return
                if w == old_w:
                    return w + 2
                old_w = w
                w = 0

    def _draw_poly(self, poly_points, color, overwrite=True):
        poly = Polygon([p.to_coord() for p in poly_points])
        for x in range(self.drawing_bound.w):
            for y in range(self.drawing_bound.h):
                pt = Point(x, y)
                if poly.contains(pt):
                    if overwrite:
                        self.draw_pixel(x, y, color)
                    else:
                        self.draw_pixel_safe(x, y, color)

    def debug_poly(self, poly_node):
        for i, p in enumerate(poly_node):
            c = Color.hsv2rgb(int((i/len(poly_node))*360), 1, 1)
            self.draw_pixel(p.x, p.y, c)

