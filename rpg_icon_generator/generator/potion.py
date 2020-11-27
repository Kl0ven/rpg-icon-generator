from rpg_icon_generator.utils.vector import Vector
import math
from rpg_icon_generator.utils.color import Color
from rpg_icon_generator.generator.__generator import Generator


class Potion_Generator(Generator):
    def generate(self, seed, dimension, render_scale, output_directory, complexity):
        self.reset_canvas(dimension, render_scale, output_directory)
        self.set_seed(seed)
        self.set_drawing_bound(dimension, complexity)
        
        width = self.turtle_bound.w
        height = self.turtle_bound.h
        centerXL = (width/2-1) + self.turtle_bound.x

        # height of bottle lip
        lipHeight = math.ceil(self.random.randomRange(2, 5) * self.dscale)
        # height of stopper sticking out of bottle
        stopperTopHeight = math.ceil(self.random.randomRange(2, 5) * self.dscale)
        # depth of stopper into the bottle
        stopperDepth = self.random.randomRange(lipHeight + 1, lipHeight + math.floor(4 * self.dscale))
        # width of stopper inside bottle
        stopperWidth = math.ceil(self.random.randomRange(2, 6) * self.dscale) * 2
        # width of bottle neck
        neckWidth = stopperWidth + 2
        # width of bottle lip
        lipWidth = neckWidth + math.ceil(self.random.randomRange(2, 4) * self.dscale) * 2
        # width of outer stopper
        stopperTopWidth = min(stopperWidth + 2, lipWidth - 2)
        # top of stopper
        stopperTop = self.turtle_bound.y
        # top of lip
        lipTop = stopperTop + stopperTopHeight
        # top of neck
        neckTop = lipTop + lipHeight
        # bottom of bottle
        bottleBottom = self.turtle_bound.y + height
        # fluid start
        fluidTop = neckTop + \
            self.random.randomRangeFloat(height/8, (bottleBottom-neckTop)*0.6)
        # min dist between contour changes
        contourInterval = math.floor(4 * self.dscale)

        stopperLight = Color(222, 152, 100)
        stopperDark = Color(118, 49, 0)

        innerBorderLight = Color(213, 226, 239)
        innerBorderDark = Color(181, 196, 197)

        glassLight = Color(227, 244, 248, 165/255)
        glassDark = Color(163, 187, 199,  165/255)

        fluidColor = Color.random_color(self.random)
        fluidColor2 = fluidColor.copy().colorRandomize(300, self.random)

        # generate shape of neck/body
        contour = [None for i in range(bottleBottom+1)]
        contour[neckTop] = neckWidth/2
        velocity = 0
        acceleration = 0
        direction = 1
        bodyTop = neckTop + 1
        for b in range(bodyTop, bottleBottom+1):
            d = math.floor(velocity)
            velocity += acceleration
            contour[b] = max(neckWidth/2, min(width/2-2, contour[b-1]+d))
            if b % contourInterval == 0 and self.random.randomFloat()<=0.5:
                acceleration = direction * self.random.randomRange(0,5)/2
                direction = -direction

        # draw outer stopper
        stopperLeft = centerXL - stopperTopWidth/2 + 1
        for x in range(stopperTopWidth):
            n = (x / (stopperTopWidth - 1))-0.5
            color = Color.colorLerp(stopperLight, stopperDark, n)
            self.fill_rect(int(x + stopperLeft), int(stopperTop), 1, int(stopperTopHeight), color)
        
        # draw body
        previousContour = lipWidth
        for y in range(neckTop, len(contour)):
            contourWidth = int(contour[y]*2)

            # draw fluid
            if y > fluidTop:
                vn = (y - fluidTop) / (bottleBottom - fluidTop)
                left = int(centerXL - contourWidth/2)
                for x in range(1, contourWidth):
                    n = x/(contourWidth-1)-(0.5+self.random.randomFloat()*0.1)
                    color = Color.colorLerp(
                                Color.colorLerp(fluidColor, fluidColor2, vn),
                                Color.colorLerp(
                                    fluidColor.copy().colorDarken(1), 
                                    fluidColor2.copy().colorDarken(1), 
                                    vn
                                ),
                                n
                            )
                    self.draw_pixel(left + x, y, color)
            
            # draw glass
            if y >= neckTop and y <= fluidTop:
                left = int(centerXL - contourWidth/2)
                for x in range(1, contourWidth):
                    n = x/(contourWidth-1)
                    color = Color.colorLerp(glassLight, glassDark, n)
                    self.draw_pixel(left + x, y, color)

            if contourWidth == previousContour:
                # contour is the same
                self.draw_pixel(int(centerXL - contourWidth/2 + 1), y, innerBorderLight)
                self.draw_pixel(int(centerXL + contourWidth/2), y, innerBorderDark)
            else:
                yOff = y-1 if previousContour < contourWidth else y
                yInner = y if previousContour < contourWidth else y-1
                minContour = min(contourWidth, previousContour)
                lineWidth = abs(previousContour - contourWidth)/2
                lineOffset = lineWidth-1
                self.fill_rect(centerXL - minContour/2 - lineWidth + 1, yInner, lineWidth, 1, innerBorderLight)
                self.draw_pixel(centerXL - contourWidth/2 + 1, y, innerBorderLight)
                self.fill_rect(centerXL + minContour/2 + 1, yInner, lineWidth, 1, innerBorderLight)
                self.draw_pixel(centerXL + contourWidth/2, y, innerBorderLight)
            
            previousContour = contourWidth

        # draw overlay stuff
        previousContour = lipWidth
        for y in range(neckTop, len(contour)):
            contourWidth = contour[y]*2
            # draw top-left reflection
            if previousContour < contourWidth:
                reflectWidth = max(1, contourWidth - previousContour)
                # crunch toward middle
                crunch = 1 - 0.3 * contourWidth / width
                reflectOffset = round((2 - contourWidth/2) * crunch)
                self.fill_rect(centerXL + reflectOffset, y + 2, reflectWidth * crunch, 1, Color(255, 255, 255, 0.5))
            previousContour = contourWidth

        # draw inner stopper
        stopperInnerLeft = centerXL - stopperWidth/2 + 1
        for x in range(stopperWidth):
            n = (x / (stopperWidth - 1))-0.5
            c = Color.colorLerp(stopperLight, stopperDark, n)
            self.fill_rect(x + stopperInnerLeft, lipTop, 1, stopperDepth, c)

        # draw lip (over stopper)
        lipLeft = centerXL - lipWidth/2 + 1
        self.fill_rect(lipLeft, lipTop, 1, lipHeight, innerBorderLight)
        self.fill_rect(lipLeft + lipWidth - 1, lipTop, 1, lipHeight, innerBorderDark)
        for x in range(1, lipWidth-1):
            n = ((x-1) / (lipWidth-3))-0.5
            self.fill_rect(x + lipLeft, lipTop, 1, lipHeight, Color.colorLerp(glassLight, glassDark, n))

        # draw bottom border
        borderLeft = centerXL - contour[bottleBottom] + 1
        borderWidth = int(contour[bottleBottom]*2)
        for x in range(borderWidth):
            n = (x/(borderWidth-1))-0.5
            self.draw_pixel(borderLeft + x, bottleBottom, Color.colorLerp(innerBorderLight, innerBorderDark, n))

        self._draw_border()
        self._draw_rarity_border(complexity)
        self.export(seed)
