/** Selectors for customer dashboard, deposit/withdraw forms, and transactions list. */
export const CustomerLocators = {
  depositButton: 'button:has-text("Deposit")',
  withdrawButton: 'button:has-text("Withdrawl")',
  transactionsButton: 'button:has-text("Transactions")',
  backButton: 'button:has-text("Back")',
  resetButton: 'button:has-text("Reset")',
  accountSelect: '#accountSelect',
  balanceValue: 'div.center strong:nth-of-type(2)',
  accountCenterText: 'div.center[ng-hide="noAccount"]',
  amountInput: 'input[ng-model="amount"]',
  formSubmitButton: 'form button[type="submit"]',
  messageSpan: 'span[ng-show="message"]',
  transactionsTable: 'table.table-bordered',
  transactionsTableBodyRows: 'table.table-bordered tbody tr',
} as const;
