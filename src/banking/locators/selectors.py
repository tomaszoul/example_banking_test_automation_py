"""Central selector registry for XYZ Banking Project demo app."""


class HomePage:
    heading = "strong.mainHeading"
    customer_login_btn = 'button[ng-click="customer()"]'
    manager_login_btn = 'button[ng-click="manager()"]'


class CustomerLoginPage:
    user_select = "#userSelect"
    login_btn = 'button[type="submit"]'


class CustomerDashboard:
    welcome_name = "span.fontBig"
    account_number = 'div.center[ng-hide="noAccount"] strong:nth-of-type(1)'
    balance = 'div.center[ng-hide="noAccount"] strong:nth-of-type(2)'
    currency = 'div.center[ng-hide="noAccount"] strong:nth-of-type(3)'
    account_select = "#accountSelect"
    transactions_btn = 'button[ng-click="transactions()"]'
    deposit_btn = 'button[ng-click="deposit()"]'
    withdraw_btn = 'button[ng-click="withdrawl()"]'
    logout_btn = 'button[ng-click="byebye()"]'


class DepositPageSelectors:
    amount_input = 'input[ng-model="amount"]'
    submit_btn = 'form button[type="submit"]'
    success_message = 'span[ng-show="message"]'


class WithdrawPageSelectors:
    amount_input = 'input[ng-model="amount"]'
    submit_btn = 'form button[type="submit"]'
    message = 'span[ng-show="message"]'


class TransactionsPage:
    table = "table.table-bordered"
    start_date_input = "#start"
    end_date_input = "#end"
    table_rows = "tbody tr"
    reset_btn = 'button[ng-click="reset()"]'
    back_btn = 'button[ng-click="back()"]'


class ManagerPageSelectors:
    add_customer_tab = 'button[ng-click="addCust()"]'
    open_account_tab = 'button[ng-click="openAccount()"]'
    customers_tab = 'button[ng-click="showCust()"]'
    first_name_input = 'input[ng-model="fName"]'
    last_name_input = 'input[ng-model="lName"]'
    post_code_input = 'input[ng-model="postCd"]'
    add_customer_btn = 'button[ng-click="addCustomer()"]'
    customer_select = "#userSelect"
    currency_select = "#currency"
    process_btn = 'button[ng-click="process()"]'
    search_input = 'input[ng-model="searchCustomer"]'
    customers_table = "table.table-bordered"
    delete_btn = 'button[ng-click="deleteCust(cust)"]'
