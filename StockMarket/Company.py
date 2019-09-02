class Company():

    def __init__(self):

        #Stores the financial information for each stock
        self.company = {'doc_type':'None', 'name':'None', 'trading_symbol':'None', 'annual_dividend_yield':'None', 'date':'None', 'shares_outstanding':'None',
        'shares_diluted':'None', 'shares_basic':'None', 'statement_type':'None', 'revenue':'None', 'cost_of_sales':'None', 'gross_profit':'None', 'operating_income':'None',
        'total_operating_expense':'None', 'income_before_taxes':'None', 'income_after_taxes':'None', 'earnings_per_share_basic':'None', 'earnings_per_share_diluted':'None',
        'comprehensive_income':'None', 'current_assets':'None', 'current_liabilities':'None', 'short_term_debt':'None', 'long_term_debt':'None', 'retained_earnings':'None',
        'common_equity':'None', 'total_shareholders_equity':'None', 'preferred_dividend':'None', 'dividends_paid':'None', 'dividend_per_share':'None', 'revenue_growth':'None',
        'cash_equivalent': 'None', 'change_in_cash':'None', 'total_assets':'None', 'total_liabilities':'None', 'total_operating_cash_flow':'None', 'gross_profit_margin':'None',
        'operating_profit_margin':'None', 'net_profit_margin':'None', 'cash_return_on_assets':'None', 'return_on_common_equity':'None', 'return_on_debt':'None',
        'return_on_capital':'None', 'return_on_earnings':'None', 'rating':'None', 'dividend_growth_rate':'None', 'dividend_payout_ratio':'None'}
        #Saves the evaluation rating of the company
        self.rating = 0

   # Convert the company object to string value so it can be printed
    def __str__(self):
        output = ""
        output += "doc type : " + str(self.doc_type) + "\n"
        output += "rating : " + str(self.rating) + "\n"
        output += "name : " + str(self.name) + "\n"
        output += "date : " + str(self.date) + "\n"
        output += "trading symbol : " + str(self.trading_symbol) + "\n"
        output += "annual dividend yield : " + str(self.annual_dividend_yield) + "\n"
        output += "dividend growth rating : " + str(self.dividend_growth_rate) + "\n"
        output += "dividend payout ratio : " + str(self.dividend_payout_ratio) + "\n"
        output += "revenue : " + str(self.revenue) + "\n"
        output += "cost of sales : " +str(self.cost_of_sales) + "\n"      
        output += "gross profit : " + str(self.gross_profit) + "\n"
        output += "operating income : " + str(self.operating_income) + "\n"
        output += "total operating expense : " + str(self.total_operating_expense) + "\n"
        output += "total operating cash flow : " + str(self.total_operating_cash_flow) + "\n"
        output += "comprehensive income : " + str(self.comprehensive_income) + "\n"
        output += "current assets : " + str(self.current_assets) + "\n"
        output += "current liabilities : " + str(self.current_liabilities) + "\n"
        output += "dividends paid : " + str(self.dividends_paid) + "\n"
        output += "income before taxes : " + str(self.income_before_taxes) + "\n"
        output += "income after taxes : " + str(self.income_after_taxes) + "\n"
        output += "total assets : " + str(self.total_assets) + "\n"
        output += "total liabilities : " + str(self.total_liabilities) + "\n"
        output += "short term debt : " + str(self.short_term_debt) + "\n"
        output += "long term debt : " + str(self.long_term_debt) + "\n"
        output += "retained earnings : " + str(self.retained_earnings) + "\n"
        output += "common equity : " + str(self.common_equity) + "\n"
        output += "total shareholders equity : " + str(self.total_shareholders_equity) + "\n"
        output += "shares outstanding : " + str(self.shares_outstanding) + "\n"
        output += "cash equivalent : " + str(self.cash_equivalent) + "\n"
        output += "change in cash : " + str(self.change_in_cash) + "\n"
        output += "revenue_growth : " + str(self.revenue_growth) + "\n"
        output += "gross_profit_margin : " + str(self.gross_profit_margin) + "\n"
        output += "operating_profit_margin : " + str(self.operating_profit_margin) + "\n"
        output += "net_profit_margin : " + str(self.net_profit_margin) + "\n"
        output += "cash_return_on_assets : " + str(self.cash_return_on_assets) + "\n"
        output += "return_on_common_equity : " + str(self.return_on_common_equity) + "\n"
        output += "return_on_debt : " + str(self.return_on_debt) + "\n"
        output += "return_on_capital : " + str(self.return_on_capital) + "\n"
        output += "return_on_earnings : " + str(self.return_on_earnings) + "\n"

        return output
        
#####################################################
##########            Getters            ############
#####################################################
    @property
    def doc_type(self):
        return self.company['doc_type']

    @property
    def name(self):
        return self.company['name']

    @property
    def date(self):
        return self.company['date']

    @property
    def rating(self):
        return self.company['rating']
    
    @property
    def trading_symbol(self):
        return self.company['trading_symbol']
    
    @property
    def annual_dividend_yield(self):
        return self.company['annual_dividend_yield']

    @property
    def dividend_growth_rate(self):
        return self.company['dividend_growth_rate']

    @property
    def dividend_payout_ratio(self):
        return self.company['dividend_payout_ratio']
    
    @property
    def shares_outstanding(self):
        return self.company['shares_outstanding']
    
    @property
    def shares_diluted(self):
        return self.company['shares_diluted']
    
    @property
    def shares_basic(self):
        return self.company['shares_basic']
    
    @property
    def statement_type(self):
        return self.company['statement_type']
    
    @property
    def revenue(self):
        return self.company['revenue']
    
    @property
    def cost_of_sales(self):
        return self.company['cost_of_sales']
    
    @property
    def gross_profit(self):
        return self.company['gross_profit']
    
    @property
    def operating_income(self):
        return self.company['operating_income']

    @property
    def total_operating_cash_flow(self):
        return self.company['total_operating_cash_flow']
    
    @property
    def total_operating_expense(self):
        return self.company['total_operating_expense']
    
    @property
    def income_before_taxes(self):
        return self.company['income_before_taxes']
    
    @property
    def income_after_taxes(self):
        return self.company['income_after_taxes']
    
    @property
    def earnings_per_share_basic(self):
        return self.company['earnings_per_share_basic']
    
    @property
    def earnings_per_share_diluted(self):
        return self.company['earnings_per_share_diluted']
    
    @property
    def comprehensive_income(self):
        return self.company['comprehensive_income']
    
    @property
    def current_assets(self):
        return self.company['current_assets']

    @property
    def cash_equivalent(self):
        return self.company['cash_equivalent']

    @property
    def change_in_cash(self):
        return self.company['change_in_cash']
    
    @property
    def current_liabilities(self):
        return self.company['current_liabilities']
    
    @property
    def total_assets(self):
        return self.company['total_assets']
    
    @property
    def total_liabilities(self):
        return self.company['total_liabilities']
    
    @property
    def short_term_debt(self):
        return self.company['short_term_debt']
    
    @property
    def long_term_debt(self):
        return self.company['long_term_debt']
    
    @property
    def retained_earnings(self):
        return self.company['retained_earnings']
    
    @property
    def common_equity(self):
        return self.company['common_equity']
    
    @property
    def total_shareholders_equity(self):
        return self.company['total_shareholders_equity']
    
    @property
    def preferred_dividend(self):
        return self.company['preferred_dividend']
    
    @property
    def dividends_paid(self):
        return self.company['dividends_paid']
    
    @property
    def dividend_per_share(self):
        return self.company['dividend_per_share']

    @property
    def revenue_growth(self):
        return self.company['revenue_growth']

    @property
    def gross_profit_margin(self):
        return self.company['gross_profit_margin']

    @property
    def operating_profit_margin(self):
        return self.company['operating_profit_margin']

    @property
    def net_profit_margin(self):
        return self.company['net_profit_margin']

    @property
    def cash_return_on_assets(self):
        return self.company['cash_return_on_assets']

    @property
    def return_on_common_equity(self):
        return self.company['return_on_common_equity']

    @property
    def return_on_debt(self):
        return self.company['return_on_debt']

    @property
    def return_on_capital(self):
        return self.company['return_on_capital']

    @property
    def return_on_earnings(self):
        return self.company['return_on_earnings']
    
#####################################################
##########            Setters            ############
#####################################################

    @doc_type.setter
    def doc_type(self, doc_type):
        self.company['doc_type'] = doc_type

    @name.setter
    def name(self, name):
        self.company['name'] = name

    @date.setter
    def date(self, date):
        self.company['date'] = date

    @rating.setter
    def rating(self, rating):
        self.company['rating'] = rating
        
    @trading_symbol.setter
    def trading_symbol(self, trading_symbol):
        self.company['trading_symbol'] = trading_symbol
        
    @annual_dividend_yield.setter
    def annual_dividend_yield(self, dividend_yield):
        self.company['annual_dividend_yield'] = dividend_yield

    @dividend_growth_rate.setter
    def dividend_growth_rate(self, dividend_growth_rate):
        self.company['dividend_growth_rate'] = dividend_growth_rate

    @dividend_payout_ratio.setter
    def dividend_payout_ratio(self, dividend_payout_ratio):
        self.company['dividend_payout_ratio'] = dividend_payout_ratio
        
    @shares_outstanding.setter
    def shares_outstanding(self, shares_outstanding):
        self.company['shares_outstanding'] = shares_outstanding
        
    @shares_diluted.setter
    def shares_diluted(self, shares_diluted):
        self.company['shares_diluted'] = shares_diluted
        
    @shares_basic.setter
    def shares_basic(self, shares_basic):
        self.company['shares_basic'] = shares_basic
        
    @statement_type.setter
    def statement_type(self, statement_type):
        self.company['statement_type'] = statement_type
        
    @revenue.setter
    def revenue(self, revenue):
        self.company['revenue'] = revenue
        
    @cost_of_sales.setter
    def cost_of_sales(self, cost_of_sales):
        self.company['cost_of_sales'] = cost_of_sales
        
    @gross_profit.setter
    def gross_profit(self, gross_profit):
        self.company['gross_profit'] = gross_profit
        
    @operating_income.setter
    def operating_income(self, operating_income):
        self.company['operating_income'] = operating_income

    @total_operating_cash_flow.setter
    def total_operating_cash_flow(self, total_operating_cash_flow):
        self.company['total_operating_cash_flow'] = total_operating_cash_flow
        
    @total_operating_expense.setter
    def total_operating_expense(self, total_operating_expense):
        self.company['total_operating_expense'] = total_operating_expense
        
    @income_before_taxes.setter
    def income_before_taxes(self, income_before_taxes):
        self.company['income_before_taxes'] = income_before_taxes
        
    @income_after_taxes.setter
    def income_after_taxes(self, income_after_taxes):
        self.company['income_after_taxes'] = income_after_taxes
        
    @earnings_per_share_basic.setter
    def earnings_per_share_basic(self, earnings_per_share_basic):
        self.company['earnings_per_share_basic'] = earnings_per_share_basic
        
    @earnings_per_share_diluted.setter
    def earnings_per_share_diluted(self, earnings_per_share_diluted):
        self.company['earnings_per_share_diluted'] = earnings_per_share_diluted
        
    @comprehensive_income.setter
    def comprehensive_income(self, comprehensive_income):
        self.company['comprehensive_income'] = comprehensive_income
        
    @current_assets.setter
    def current_assets(self, current_assets):
        self.company['current_assets'] = current_assets

    @cash_equivalent.setter
    def cash_equivalent(self, cash_equivalent):
        self.company['cash_equivalent'] = cash_equivalent

    @change_in_cash.setter
    def change_in_cash(self, change_in_cash):
        self.company['change_in_cash'] = change_in_cash
        
    @current_liabilities.setter
    def current_liabilities(self, current_liabilities):
        self.company['current_liabilities'] = current_liabilities
        
    @total_assets.setter
    def total_assets(self, total_assets):
        self.company['total_assets'] = total_assets
        
    @total_liabilities.setter
    def total_liabilities(self, total_liabilities):
        self.company['total_liabilities'] = total_liabilities
        
    @short_term_debt.setter
    def short_term_debt(self, short_term_debt):
        self.company['short_term_debt'] = short_term_debt
        
    @long_term_debt.setter
    def long_term_debt(self, long_term_debt):
        self.company['long_term_debt'] = long_term_debt
        
    @retained_earnings.setter
    def retained_earnings(self, retained_earnings):
        self.company['retained_earnings'] = retained_earnings
        
    @common_equity.setter
    def common_equity(self, common_equity):
        self.company['common_equity'] = common_equity
        
    @total_shareholders_equity.setter
    def total_shareholders_equity(self, total_shareholders_equity):
        self.company['total_shareholders_equity'] = total_shareholders_equity
        
    @preferred_dividend.setter
    def preferred_dividend(self, preferred_dividend):
        self.company['preferred_dividend'] = preferred_dividend
        
    @dividends_paid.setter
    def dividends_paid(self, dividends_paid):
        self.company['dividends_paid'] = dividends_paid
        
    @dividend_per_share.setter
    def dividend_per_share(self, dividend_per_share):
        self.company['dividend_per_share'] = dividend_per_share

    @revenue_growth.setter
    def revenue_growth(self, revenue_growth):
        self.company['revenue_growth'] = revenue_growth

    @gross_profit_margin.setter
    def gross_profit_margin(self, gross_profit_margin):
        self.company['gross_profit_margin'] = gross_profit_margin

    @operating_profit_margin.setter
    def operating_profit_margin(self, operating_profit_margin):
        self.company['operating_profit_margin'] = operating_profit_margin

    @net_profit_margin.setter
    def net_profit_margin(self, net_profit_margin):
        self.company['net_profit_margin'] = net_profit_margin

    @cash_return_on_assets.setter
    def cash_return_on_assets(self, cash_return_on_assets):
        self.company['cash_return_on_assets'] = cash_return_on_assets

    @return_on_common_equity.setter
    def return_on_common_equity(self, return_on_common_equity):
        self.company['return_on_common_equity'] = return_on_common_equity

    @return_on_debt.setter
    def return_on_debt(self, return_on_debt):
        self.company['return_on_debt'] = return_on_debt

    @return_on_capital.setter
    def return_on_capital(self, return_on_capital):
        self.company['return_on_capital'] = return_on_capital

    @return_on_earnings.setter
    def return_on_earnings(self, return_on_earnings):
        self.company['return_on_earnings'] = return_on_earnings

########################################################
#######     Calculate Operating Profitablilty  #########
########################################################
    def is_negative_number(self, number):
        """
        Returns true if number is negative and false if number is positive.

        Keyword arguments:
        number -- interger or float value to evaluate
        """
        multiple = ['1']
        is_negative = False
        decimal_places = 0
        value = str(number)
        try:
            if '.' in value:
                value = value.split('.')
                decimal_places = len(value[1])

                for x in range(decimal_places):
                    multiple.append('0')

                multiple = ''.join(multiple)
                multiple = float(multiple)

                if float(number) * multiple < 0:
                    is_negative = True
            else:
                if float(number) < 0:
                    is_negative = True

        except Exception as ex:
            try:
                print(ex.message)
            except:
                print(ex)

        return is_negative
    
    #Used to assign a rating value from 1 to 1000 for each operating profitability ratio
    def sigmoid(self, value):
        """
        Returns a value from 1 - 1000.
        Returns 0 if input value is a negative number or input value is zero

        Keyword arguments:
        value -- interger or float value to evaluate
        """
        import math
        if self.is_negative_number(value) or value == 0:
            return 0
        else:
            return 1000 / (1 + math.exp(-value))
  
    #Calculates the gross profit margin ratio
    def calculate_gross_profit_margin(self):
        """
        Returns the gross profit margin ratio of the company.

        Keyword arguments: None
        """
        revenue = 0
        COGS = 0
        GPM = 0
        try:
            revenue = float(self.revenue)
            COGS = float(self.cost_of_sales)
            if revenue != 0 and COGS != 0:
                GPM = (revenue - COGS)/revenue
            else:
                print(f'Missing Records! \nRevenue : {revenue} \ncost_of_sales : {COGS}')
        except:
            pass

        finally:
            return GPM

    #Calculates the operating profit margin ratio
    #includes Amortization and Depreciation
    def calculate_operating_profit_margin(self):
        """
        Returns the operating profit margin ratio of the company.
        
        Keyword arguments: None
        """
        operating_income = 0
        revenue = 0
        OPM = 0
        try:
            revenue = float(self.revenue)
            operating_income = float(self.operating_income)
            if revenue != 0 and operating_income != 0:
                OPM = operating_income / revenue 
            else:
                print(f'Missing Records! \noperating_income : {operating_income} \nrevenue : {revenue}')
        except:
            pass
        
        finally:
            return OPM

    #Calculates the net profit margin ratio
    #should be compared over a period of time 
    def calculate_net_profit_margin(self):
        """
        Returns the net profit margin ratio of the company.
        
        Keyword arguments: None
        """
        net_profit = 0
        revenue = 0
        NPM = 0
        try:
            revenue = float(self.revenue)
            net_profit = float(self.income_after_taxes)
            if revenue != 0 and net_profit != 0:
                NPM = net_profit / revenue
            else:
                print(f'Missing Records! \nnet_profit : {net_profit} \nrevenue : {revenue}')
        except:
            pass
        
        finally:
            return NPM

    #Calculates the return on asset - measures how efficiently a company uses it's assets
    #divergence between ROA and Cash ROA in longterm indicates company is manipulating income
    def calculate_cash_return_on_assets(self):
        """
        Returns the cash return on assets ratio of the company.
        
        Keyword arguments: None
        """
        operating_cash_flow = 0
        total_assets = 0
        CROA = 0
        try:
            total_assets = float(self.total_assets)
            operating_cash_flow = float(self.total_operating_cash_flow)
            if operating_cash_flow != 0 and total_assets != 0:
                CROA = operating_cash_flow / total_assets
            else:
                print(f'Missing Records! \noperating_cash_flow : {operating_cash_flow} \ntotal_assets : {total_assets}')
        except:
            pass

        finally:
            return CROA

    #Calculates the return on common equity - measures profit generated from shareholder's funds
    def calculate_return_on_common_equity(self):
        """
        Returns the return on equity ratio of the company.
        
        Keyword arguments: None
        """
        net_income = 0
        common_equity = 0
        preferred_dividend = 0
        ROCE = 0
        try:
            common_equity = float(self.common_equity) 
            net_income = float(self.income_after_taxes)         
            if self.preferred_dividend != 'None':
                preferred_dividend = float(self.preferred_dividend) 

            if net_income != 0 and common_equity != 0:
                ROCE = (net_income - preferred_dividend) / common_equity
            else:
                print(f'Missing Records! \nnet_income : {net_income} \ncommon_equity : {common_equity}') 
        except:
            pass
          
        finally:
            return ROCE

    #Measures profit generated from debt
    def calculate_return_on_debt(self):
        """
        Returns the return on debt ratio of the company.
        
        Keyword arguments: None
        """
        net_income = 0
        long_term_debt = 0
        ROD = 0
        try:
            net_income = float(self.income_after_taxes)
            long_term_debt = float(self.long_term_debt)

            if net_income != 0 and long_term_debt != 0:
                ROD = net_income / long_term_debt
            else:
                print(f'Missing Records! \nnet_income : {net_income} \nlong_term_debt : {long_term_debt}') 
        except:
            pass
        
        finally:
            return ROD
    
    #Measures how well company uses its capital: (better measure of operating profitability than ROE)
    def calculate_return_on_capital(self):
        """
        Returns the return on capital ratio of the company.
        
        Keyword arguments: None
        """
        earnings_before_taxes = 0
        current_liability = 0
        total_assets = 0
        ROC = 0
        try:
            total_assets = float(self.total_assets)
            current_liability = float(self.current_liabilities)
            earnings_before_taxes = float(self.income_before_taxes)

            if earnings_before_taxes != 0 and total_assets != 0 and current_liability != 0:
                assets = total_assets - current_liability
                if assets > 0:
                    ROC = earnings_before_taxes / assets
            else:
                print(f'Missing Records! \nearnings_before_taxes : {earnings_before_taxes} \ntotal_assets : {total_assets} \ncurrent_liability : {current_liability}') 
        except:
            pass

        finally:
            return ROC

    #Measures how well a company uses its retained earnings (should be measured over 5 to 10 years period)
    def calculate_return_on_earnings(EPS_current_year, EPS_previous_year, EPS_diluted, dividend_per_share):
        """
        Returns the return on earnings ratio of the company.
        
        Keyword arguments: (Integer or Float)
        EPS_current_year -- current year Earnings Per Share
        EPS_previous_year -- previous year Earnings Per Share
        EPS_diluted -- diluted Earnings Per Share
        dividend_per_share -- Dividend Per Share
        """
        try:
            ROE = 0
            if (EPS_diluted - dividend_per_share) != 0:
                ROE = (EPS_current_year - EPS_previous_year) / (EPS_diluted - dividend_per_share)
        except Exception as ex:
            try:
                print(ex.message)
            except:
                print(ex)
        finally:
            return ROE

    #Update rating matrix for evaluating companies
    def update_matrix(self):
        """
        Update all company evaluation ratio

        Return: None
        
        Keyword arguments: None
        """
        count = 0
        rating = 0

        if self.revenue != 'None' and self.cost_of_sales != 'None':
            self.gross_profit_margin = self.calculate_gross_profit_margin()

        if self.operating_income != 'None' and self.revenue != 'None':
            self.operating_profit_margin = self.calculate_operating_profit_margin()

        if self.income_after_taxes != 'None' and self.revenue != 'None':
            self.net_profit_margin = self.calculate_net_profit_margin()

        if self.total_operating_cash_flow != 'None' and self.total_assets != 'None':
            self.cash_return_on_assets = self.calculate_cash_return_on_assets()

        if self.income_after_taxes != 'None' and self.common_equity != 'None':
            self.return_on_common_equity = self.calculate_return_on_common_equity()

        if self.income_after_taxes != 'None' and self.long_term_debt != 'None':
            self.return_on_debt = self.calculate_return_on_debt()

        if self.income_before_taxes != 'None' and self.total_assets != 'None' and self.current_liabilities != 'None':
            self.return_on_capital = self.calculate_return_on_capital()

        if self.gross_profit_margin != 'None':
            rating += self.sigmoid(self.gross_profit_margin)
            count += 1

        if self.operating_profit_margin != 'None':
            rating += self.sigmoid(self.operating_profit_margin)
            count += 1

        if self.net_profit_margin != 'None':
            rating += self.sigmoid(self.net_profit_margin)
            count += 1

        if self.cash_return_on_assets != 'None':
            rating += self.sigmoid(self.cash_return_on_assets)
            count += 1

        if self.return_on_common_equity != 'None':
            rating += self.sigmoid(self.return_on_common_equity)
            count += 1

        if self.return_on_debt != 'None':
            rating += self.sigmoid(self.return_on_debt)
            count += 1

        if self.return_on_capital != 'None':
            rating += self.sigmoid(self.return_on_capital)
            count += 1

        if self.revenue_growth != 'None':
            rating += self.sigmoid(self.revenue_growth)
            count += 1

        if count > 0:
            rating /= count
            self.rating = rating

        count = 0
        rating = 0

        #Assign a rating penalty for any company with negative income
        if self.income_after_taxes != 'None':
            try:
                if float(self.income_after_taxes) < 0:
                    rating -= 1000
                    count += 1
            except:
                pass

        if self.total_operating_cash_flow != 'None':
            try:
                if float(self.total_operating_cash_flow) < 0:
                    rating -= 1000
                    count += 1
            except:
                pass

        if count > 0:
            rating /= count
            self.rating += rating
