class FinanceDude:
    @staticmethod
    def calculate_subtotal(price, quantity, finance_tax_rate):
        """
        Calculate subtotal of for example an invoice or order item
        :param price: Decimal or Float
        :param quantity: Decimal, Float or Int
        :param finance_tax_rate: models.FinanceTaxRate object
        :return: float representing subtotal
        """
        # If tax is included in price, first remove it.
        price = float(price)
        if finance_tax_rate:
            if finance_tax_rate.rate_type == "IN":
                # divide price by 1.tax_percentage and then multiply by quantity
                percentage = (float(finance_tax_rate.percentage) / 100) + 1
                price = price / percentage

        return float(price) * float(quantity)

    @staticmethod
    def calculate_tax(subtotal, finance_tax_rate):
        """
        Calculate tax of for example an invoice item or order item
        :param subtotal: Decimal or float
        :param finance_tax_rate: models.FinanceTaxRate object
        :return: float representing tax or 0
        """
        if finance_tax_rate:
            percentage = (finance_tax_rate.percentage / 100)

            return float(subtotal) * float(percentage)
        else:
            return 0

    @staticmethod
    def calculate_total(subtotal, tax):
        """
        Calculate total of for example an invoice item or order item
        :param subtotal: Decimal or float
        :param tax: Decimal or float
        :return: Decimal or float of added subtotal & tax
        """
        return subtotal + tax
