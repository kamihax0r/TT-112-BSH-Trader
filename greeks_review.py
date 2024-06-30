import parameters
from account import Account

class GreeksReview:
    def __init__(self, accounts):
        self.accounts = accounts

    def review_greeks(self):
        review_results = {}
        for account in self.accounts:
            net_liq = account.get_balance().get('net_liquidating_value', 0)
            greeks = account.get_account_greeks()

            delta = greeks.get('delta', 0)
            theta = greeks.get('theta', 0)
            buying_power = account.get_balance().get('buying_power', 0)

            delta_status = self.evaluate_greek(delta, net_liq, parameters.MAX_DELTA_PCT)
            theta_status = self.evaluate_greek(theta, net_liq, parameters.MAX_THETA_PCT)
            bp_used_status = self.evaluate_buying_power(buying_power, net_liq, parameters.MAX_BUYING_POWER_PCT)

            review_results[account.account_number] = {
                'delta': {'value': delta, 'status': delta_status},
                'theta': {'value': theta, 'status': theta_status},
                'buying_power': {'value': buying_power, 'status': bp_used_status}
            }

        return review_results

    def evaluate_greek(self, value, net_liq, max_pct):
        max_value = max_pct * net_liq
        if value > max_value:
            return 'too high'
        elif value < -max_value:
            return 'too low'
        else:
            return 'ok'

    def evaluate_buying_power(self, buying_power, net_liq, max_pct):
        max_bp = max_pct * net_liq
        if buying_power > max_bp:
            return 'too high'
        else:
            return 'ok'
