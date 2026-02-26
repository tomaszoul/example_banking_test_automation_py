/** Selectors for manager page: add customer, open account, customers list. */
export const ManagerLocators = {
  addCustomerButton: 'button[ng-click="addCust()"]',
  firstNameInput: 'input[ng-model="fName"]',
  lastNameInput: 'input[ng-model="lName"]',
  postCodeInput: 'input[ng-model="postCd"]',
  addCustomerFormSubmit: 'form[ng-submit="addCustomer()"] button',
  openAccountButton: 'button[ng-click="openAccount()"]',
  managerUserSelect: '#userSelect',
  currencySelect: '#currency',
  processButton: 'button[ng-click="process()"]',
  showCustomersButton: 'button[ng-click="showCust()"]',
  searchCustomerInput: 'input[ng-model="searchCustomer"]',
  customersTable: 'table.table-bordered',
  customersTableBodyRows: 'table.table-bordered tbody tr',
  /** Use within a row: row.locator(ManagerLocators.deleteCustomerButton) */
  deleteCustomerButton: 'button[ng-click="deleteCust(cust)"]',
} as const;
