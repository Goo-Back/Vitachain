// Mock Supabase Client for Development
// Use this when Supabase project is not available

interface MockUser {
  id: string;
  email: string;
  role: string;
  full_name: string;
}

interface MockResponse<T = any> {
  data: T | null;
  error: { message: string } | null;
}

interface MockQueryBuilder {
  select: (columns?: string) => MockQueryBuilder;
  insert: (data: any) => MockResponse;
  update: (data: any) => MockQueryBuilder;
  delete: () => MockResponse;
  eq: (column: string, value: any) => MockQueryBuilder;
  order: (column: string, options?: { ascending?: boolean }) => MockQueryBuilder;
  limit: (count: number) => MockQueryBuilder;
  single: () => Promise<MockResponse>;
  maybeSingle: () => Promise<MockResponse>;
}

const createMockQueryBuilder = (): MockQueryBuilder => ({
  select: () => createMockQueryBuilder(),
  insert: () => ({ data: null, error: null }),
  update: () => createMockQueryBuilder(),
  delete: () => ({ data: null, error: null }),
  eq: () => createMockQueryBuilder(),
  order: () => createMockQueryBuilder(),
  limit: () => createMockQueryBuilder(),
  single: async () => ({ data: null, error: null }),
  maybeSingle: async () => ({ data: null, error: null })
});

const createMockAuth = () => ({
  signIn: async ({ email, password }: { email: string; password: string }) => {
    // Mock successful login for demo
    if (email === 'demo@vitachain.com' && password === 'demo123') {
      return {
        data: {
          user: {
            id: 'demo-user-id',
            email: 'demo@vitachain.com',
            role: 'CITIZEN',
            full_name: 'Demo User'
          }
        },
        error: null
      };
    }
    return {
      data: { user: null },
      error: { message: 'Invalid credentials' }
    };
  },
  signOut: async () => ({ error: null }),
  getUser: async () => ({
    data: {
      user: {
        id: 'demo-user-id',
        email: 'demo@vitachain.com',
        role: 'CITIZEN',
        full_name: 'Demo User'
      }
    },
    error: null
  }),
  signUp: async ({ email, password, options }: any) => ({
    data: {
      user: {
        id: 'new-user-id',
        email,
        role: options?.data?.role || 'CITIZEN',
        full_name: options?.data?.full_name || 'New User'
      }
    },
    error: null
  }),
  resetPasswordForEmail: async (email: string) => ({ error: null }),
  updateUser: async (attributes: any) => ({
    data: { user: { ...attributes } },
    error: null
  }),
  onAuthStateChange: () => ({ data: { subscription: null } })
});

export const supabase = {
  auth: createMockAuth(),
  from: (table: string) => createMockQueryBuilder(),
  storage: {
    from: (bucket: string) => ({
      upload: () => ({ data: null, error: null }),
      download: () => ({ data: null, error: null }),
      getPublicUrl: () => ({ data: { publicUrl: '' }, error: null })
    })
  },
  functions: {
    invoke: async (name: string, options?: any) => ({ data: null, error: null })
  }
};

// Export for compatibility
export const createSupabaseClient = () => supabase;
export default supabase;
