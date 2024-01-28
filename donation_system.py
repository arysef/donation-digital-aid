import bisect
from datetime import datetime, timedelta
from functools import total_ordering
from typing import Optional

class ShelterDonationSystem:
    """
    A class to represent a donation system
    Sorts and stores donations by type and date.
    Includes methods to register donations and record distributions. 
    """
    @total_ordering 
    class CashDonation: 
        def __init__(self, donation_date, amount):
            self.donation_date = donation_date
            self.amount = amount
        
        def __eq__(self, other):
            return self.donation_date == other.donation_date

        def __lt__(self, other):
            return self.donation_date < other.donation_date
        
        def __str__(self):
            return self.__repr__()
        
        def __repr__(self):
            return f"({self.donation_date}, {self.amount})"

    @total_ordering
    class FoodDonation: 
        def __init__(self, donation_date, expiration_date, amount):
            self.donation_date = donation_date
            self.expiration_date = expiration_date
            self.amount = amount
        
        def __eq__(self, other):
            return self.expiration_date == other.expiration_date

        def __lt__(self, other):
            return self.expiration_date < other.expiration_date
        
        def __str__(self):
            return self.__repr__()
        
        def __repr__(self):
            return f"({self.donation_date}, {self.expiration_date}, {self.amount})"
        

    def __init__(self):
        self.donations = []
        self.food_inventory = []
        self.cash_inventory = []
        self.distributions = []

    def register_donation(self, donor_name, donation_type, amount, date, expiration_date):
        """ 
        Registers a donation in the system. Sorts to maintain chronological order to facilitate distribution consistency.
        """
        donation = {
            "donor_name": donor_name,
            "donation_type": donation_type,
            "amount": amount,
            "date": date,
            "expiration_date": expiration_date if donation_type == "Food" else ""
        }
        
        if donation_type == 'Food':
            self.food_inventory.append(self.FoodDonation(date, expiration_date, amount))
            self.food_inventory.sort()
        else:
            self.cash_inventory.append(self.CashDonation(date, amount))
            self.cash_inventory.sort()
            print(self.cash_inventory)
        
        self.donations.append(donation)
        print("Donation registered successfully.")

        

    def distribute_donation(self, distribution_type, amount, date) -> Optional[str]:
        """
        Distributes donations and checks to ensure that there is enough inventory to complete the distribution.
        Inventory is only executed if there is enough inventory to complete the distribution.
        """
        distribution = {
            "distribution_type": distribution_type,
            "amount": amount,
            "date": date
        }

        # For money distributions, checks to see if there is enough money in the system to complete the distribution
        # Only includes donations that are on or before the distribution date
        if distribution_type == 'Money':
            end = bisect.bisect_right(self.cash_inventory, self.CashDonation(date, 0))
            amount_left = amount
            end_idx = -1

            for i, metadata in enumerate(self.cash_inventory[:end]):
                if amount_left >= metadata.amount:
                    amount_left -= metadata.amount
                    end_idx = i
                else:
                    self.cash_inventory[i].amount -= amount
                    amount_left = 0
                if amount_left == 0:
                    break

            if amount_left > 0:
                return "Not enough money in system to complete distribution. Expected available money at this date: ${:.2f}".format(amount - amount_left)
            else: 
                self.cash_inventory = self.cash_inventory[end_idx + 1:]

            self.distributions.append(distribution)
            return None
        
        # Determine if there is enough food inventory on the given date
        # Only includes donations that are on or before the distribution date and are not expired
        if distribution_type == 'Food':
            start_idx = bisect.bisect_left(self.food_inventory, self.FoodDonation(date, date, 0))
            end_idx = -1
            amount_left = amount
            # Keep track of unused donations. This is required because food has restrictions on both ends (donation and distribution)
            unused = [] 

            for i, metadata in enumerate(self.food_inventory[start_idx:]):
                if metadata.expiration_date < date:
                    continue
                
                # Don't accidentally use food donated after distribution
                if metadata.donation_date > date:
                    unused.append(metadata)
                    continue

                if amount_left >= metadata.amount:
                    amount_left -= metadata.amount
                    end_idx = i
                else: 
                    self.food_inventory[i].amount -= amount_left
                    amount_left = 0
                if amount_left == 0:
                    break

            if amount_left > 0:
                return f"Not enough food expected in system to complete distribution at this date. Expected food weight on {date} is {amount - amount_left} lbs"
            else: 
                self.distributions.append(distribution)
                self.food_inventory = self.food_inventory[:start_idx] + self.food_inventory[end_idx + 1:]
                # Add back unused donations and re-sort 
                self.food_inventory.extend(unused)
                self.food_inventory.sort()
                return None

        print("Distribution recorded successfully.")

    # def generate_graph(self):
    #     """
    #     Generates a graph of donations and distributions over time.
    #     """
    #     # Find the range of dates to consider
    #     start_date = self.donations[0]["date"]

    #     # Calculate total amount for each day
    #     daily_totals = {}
    #     for single_date in (start_date + datetime.timedelta(n) for n in range(10)):
    #         total_amount = sum(donation["amount"] for donation in self.donations if donation["date"] <= single_date <= donation["expiration_date"])
    #         daily_totals[single_date] = total_amount

    #     # Prepare data for plotting
    #     dates = list(daily_totals.keys())
    #     amounts = list(daily_totals.values())

    #     return dates, amounts

    def generate_inventory_report(self):
        """
        Simple inventory that sums up all donations and distributions by type after all transactions have been recorded.
        """
        inventory = {}
        print(self.donations)
        for donation in self.donations:
            type = donation["donation_type"]
            inventory[type] = inventory.get(type, 0) + donation["amount"]
        for distribution in self.distributions:
            type = distribution["distribution_type"]
            inventory[type] -= distribution["amount"]
        
        food_daily_totals = {}
        if self.food_inventory:
            donations = sorted(self.food_inventory, key=lambda x: x.donation_date)
            # Find the range of dates to consider
            start_date = donations[0].donation_date

            # Calculate total amount for each day
            for single_date in (start_date + timedelta(n) for n in range(10)):
                total_amount = sum(donation.amount for donation in donations if donation.donation_date <= single_date <= donation.expiration_date)
                food_daily_totals[single_date] = total_amount

        return inventory, food_daily_totals

    def generate_donator_report(self):
        """
        Creates list of donations by donator and donation type.
        """
        report = {}
        for donation in self.donations:
            donor = donation["donor_name"]
            donation_type = donation["donation_type"]

            # Initialize donation_type in transposed_report if not already present
            if donation_type not in report:
                report[donation_type] = {}

            # Initialize donor for donation_type if not already present
            if donor not in report[donation_type]:
                report[donation_type][donor] = 0

            # Increment the donation amount
            report[donation_type][donor] += donation["amount"]

        return report
