/** Selectors for home / login flow (customer and manager entry). */
export const LoginLocators = {
  customerLoginButton: 'button:has-text("Customer Login")',
  bankManagerLoginButton: 'button:has-text("Bank Manager Login")',
  userSelect: 'select#userSelect',
  loginButton: 'button:has-text("Login")',
  welcomeName: 'span.fontBig',
  logoutButton: 'button:has-text("Logout")',
  /** Use with getByRole: page.getByRole('heading', { name: LoginLocators.headingXyzBankName }) */
  headingXyzBankName: /XYZ Bank/i,
} as const;
