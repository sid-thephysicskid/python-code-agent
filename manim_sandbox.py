from manim import *

class CircleToSquare(Scene):
    def construct(self):
        # Create circle
        circle = Circle(radius=2, color=BLUE)
        circle_area = MathTex(r"A = \pi r^2", color=BLUE)
        circle_area.shift(UP * 2.5)

        # Create square
        square = Square(side_length=4, color=RED)
        square_area = MathTex(r"A = s^2", color=RED)
        square_area.shift(UP * 2.5)

        # Initial setup
        self.play(
            Create(circle),
            Write(circle_area)
        )
        self.wait()

        # Transform circle to square and equation
        self.play(
            Transform(circle, square),
            Transform(circle_area, square_area)
        )
        self.wait()

        # Final pause
        self.wait()


class CircleToSquareScene(Scene):
    def construct(self):
        # Create shapes
        circle = Circle(radius=2, color=BLUE)
        square = Square(side_length=4, color=BLUE)
        
        # Create area formulas
        circle_area = MathTex(r"A = \pi r^2")
        square_area = MathTex(r"A = s^2")
        
        # Position formulas
        circle_area.next_to(circle, DOWN)
        square_area.next_to(square, DOWN)
        
        # Initial setup
        self.add(circle, circle_area)
        
        # Animation sequence
        self.play(
            Transform(circle, square),
            Transform(circle_area, square_area)
        )
        self.wait()



class ChainRuleDemoDirect(Scene):
    def construct(self):
        # Colors for different functions
        f_color = BLUE
        g_color = GREEN
        composite_color = YELLOW
        derivative_color = RED

        # Title
        title = Text("Chain Rule Demonstration", font_size=40)
        title.to_edge(UP)
        self.play(Write(title))

        # Initial functions
        f_def = MathTex("f(x) = x^2", color=f_color)
        g_def = MathTex("g(x) = \\sin(x)", color=g_color)
        fog_def = MathTex("f(g(x)) = (\\sin(x))^2", color=composite_color)

        # Position the equations
        VGroup(f_def, g_def, fog_def).arrange(DOWN, buff=0.5)
        VGroup(f_def, g_def, fog_def).next_to(title, DOWN, buff=1)

        # Show initial functions
        self.play(Write(f_def))
        self.play(Write(g_def))
        self.play(Write(fog_def))
        self.wait()

        # Chain rule statement
        chain_rule = MathTex(
            "\\frac{d}{dx}[f(g(x))] = f'(g(x)) \\cdot g'(x)",
            color=derivative_color
        )
        chain_rule.next_to(fog_def, DOWN, buff=1)

        # Show chain rule statement
        self.play(Write(chain_rule))
        self.wait()

        # Show the actual derivatives
        derivatives = VGroup(
            MathTex("f'(x) = 2x", color=f_color),
            MathTex("g'(x) = \\cos(x)", color=g_color),
            MathTex("\\frac{d}{dx}[f(g(x))] = 2\\sin(x)\\cos(x)", color=derivative_color)
        ).arrange(DOWN, buff=0.5)
        derivatives.next_to(chain_rule, DOWN, buff=1)

        # Show derivatives one by one
        for deriv in derivatives:
            self.play(Write(deriv))
            self.wait(0.5)

        # Final box around the result
        box = SurroundingRectangle(derivatives[-1], color=YELLOW)
        self.play(Create(box))
        self.wait(2)

        # Cleanup
        self.play(
            *[FadeOut(mob) for mob in self.mobjects]
        )