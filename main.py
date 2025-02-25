from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.lang import Builder

Builder.load_file('main.kv')


class MainWidget(BoxLayout):
    def switch_screen(self, screen_name):
        self.ids.screen_manager.current = screen_name

    def add_history_entry(self, entry_text):
        history_list = self.ids.history_screen.ids.history_list
        summary = entry_text.splitlines()[0]
        btn = Button(text=summary, size_hint_y=None, height=40,
                     background_color=(0.3, 0.3, 0.45, 1), font_size=16)
        btn.bind(on_release=lambda instance: self.show_history_detail(entry_text))
        history_list.add_widget(btn)

    def show_history_detail(self, detail_text):
        popup = Popup(title="Calculation Detail",
                      content=Label(text=detail_text, halign='left',
                                    valign='middle', text_size=(400, None)),
                      size_hint=(0.8, 0.8))
        popup.open()


class RefiCalculatorWidget(BoxLayout):
    result_text = StringProperty("Enter your details and click Calculate.")

    def calculate(self):
        try:
            current_loan = float(self.ids.current_loan.text)
            current_rate = float(self.ids.current_rate.text)
            remaining_term = float(self.ids.remaining_term.text)
            new_rate = float(self.ids.new_rate.text)
            new_term = float(self.ids.new_term.text)
            refi_costs = float(self.ids.refi_costs.text)
        except ValueError:
            self.result_text = "Error: Please enter valid numeric values in all fields."
            return

        if current_loan <= 0:
            self.result_text = "Error: Current Loan Amount must be greater than 0."
            return
        if remaining_term <= 0 or new_term <= 0:
            self.result_text = "Error: Loan terms (years) must be greater than 0."
            return
        if current_rate < 0 or new_rate < 0:
            self.result_text = "Error: Interest rates cannot be negative."
            return
        if refi_costs < 0:
            self.result_text = "Error: Refinance costs cannot be negative."
            return

        try:
            # Calculate current monthly payment.
            monthly_current_rate = current_rate / 100 / 12
            current_n = remaining_term * 12
            if monthly_current_rate != 0:
                current_monthly_payment = current_loan * (monthly_current_rate * (
                    1 + monthly_current_rate) ** current_n) / (((1 + monthly_current_rate) ** current_n) - 1)
            else:
                current_monthly_payment = current_loan / current_n

            total_payment_current = current_monthly_payment * current_n
            total_interest_current = total_payment_current - current_loan

            # Calculate new monthly payment.
            monthly_new_rate = new_rate / 100 / 12
            new_n = new_term * 12
            if monthly_new_rate != 0:
                new_monthly_payment = current_loan * \
                    (monthly_new_rate * (1 + monthly_new_rate) ** new_n) / \
                    (((1 + monthly_new_rate) ** new_n) - 1)
            else:
                new_monthly_payment = current_loan / new_n

            total_payment_new = new_monthly_payment * new_n
            total_interest_new = total_payment_new - current_loan

            # Calculate monthly savings and break-even period.
            monthly_savings = current_monthly_payment - new_monthly_payment
            break_even_months = refi_costs / \
                monthly_savings if monthly_savings > 0 else float('inf')

            # Generate suggestion based on calculated values.
            interest_rate_drop = current_rate - new_rate
            if monthly_savings <= 0:
                suggestion = "Suggestion: The new loan does not offer savings. Refinancing might not be beneficial."
            elif break_even_months == float('inf'):
                suggestion = "Suggestion: Unable to break even on refinance costs. Refinancing might not be recommended."
            elif break_even_months <= 12:
                suggestion = "Suggestion: Excellent! You can break even within a year. Refinancing seems highly beneficial."
            elif break_even_months <= 24:
                suggestion = "Suggestion: Good news! You can break even within two years. Consider refinancing if you plan to stay long term."
            elif break_even_months <= (remaining_term * 12) * 0.5:
                suggestion = "Suggestion: The break-even period is moderate. Consider other factors before refinancing."
            else:
                suggestion = "Suggestion: The break-even period is too long relative to your remaining term. Refinancing may not be advantageous."

            if interest_rate_drop < 0.5:
                suggestion += "\nNote: The interest rate drop is minimal, so benefits might be limited."
            elif interest_rate_drop >= 2.0:
                suggestion += "\nNote: Significant interest rate reduction detected. This refinance could yield substantial savings."

            result = (
                f"Current Monthly Payment: ${current_monthly_payment:,.2f}\n"
                f"Total Interest Remaining (Current Loan): ${total_interest_current:,.2f}\n\n"
                f"New Monthly Payment: ${new_monthly_payment:,.2f}\n"
                f"Total Interest Over New Loan: ${total_interest_new:,.2f}\n\n"
                f"Monthly Savings: ${monthly_savings:,.2f}\n"
                f"Break-even Period: {break_even_months:.1f} months\n\n"
                f"{suggestion}"
            )
            self.result_text = result

            # Log the calculation into history via MainWidget.
            from kivy.app import App
            app = App.get_running_app()
            main_widget = app.root
            main_widget.add_history_entry(result)
        except Exception as e:
            self.result_text = f"An unexpected error occurred: {str(e)}"


class HistoryScreen(BoxLayout):
    pass


class RefiCalculatorApp(App):
    def build(self):
        return MainWidget()


if __name__ == '__main__':
    RefiCalculatorApp().run()
