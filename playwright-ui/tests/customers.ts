/**
 * Customer list for parametrization. Matches Python src/banking/data/customers.py.
 * With --ui: no --full → smoke (1 customer); --full → full set (all 5 customers).
 * Same as Python: BANK_FULL_RUN=1 is set only when run_tests.py is called with --full.
 */
const ALL_CUSTOMERS = [
  'Hermoine Granger',
  'Harry Potter',
  'Ron Weasly',
  'Albus Dumbledore',
  'Neville Longbottom',
] as const;

const DEFAULT_CUSTOMER = 'Harry Potter' as const;

/** Account numbers per currency, mirroring Python Customer.accounts. */
export const CUSTOMER_ACCOUNTS: Record<string, Record<string, string>> = {
  'Hermoine Granger': { Dollar: '1001', Pound: '1002', Rupee: '1003' },
  'Harry Potter': { Dollar: '1004', Pound: '1005', Rupee: '1006' },
  'Ron Weasly': { Dollar: '1007', Pound: '1008', Rupee: '1009' },
  'Albus Dumbledore': { Dollar: '1010', Pound: '1011', Rupee: '1012' },
  'Neville Longbottom': { Dollar: '1013', Pound: '1014', Rupee: '1015' },
};

export function getCustomersForRun(): readonly string[] {
  return process.env.BANK_FULL_RUN === '1' ? ALL_CUSTOMERS : [DEFAULT_CUSTOMER];
}

export { ALL_CUSTOMERS, DEFAULT_CUSTOMER };
