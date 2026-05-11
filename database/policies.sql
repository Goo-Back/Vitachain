-- =====================================================
-- VITACHAIN SUPABASE RLS POLICIES
-- Sécurité au niveau des lignes (Row Level Security)
-- =====================================================

-- Activer RLS sur toutes les tables
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE products ENABLE ROW LEVEL SECURITY;
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;

-- =====================================================
-- TABLE PROFILES
-- =====================================================

-- Policy: Les utilisateurs peuvent voir leur propre profil
CREATE POLICY "Users can view own profile" ON profiles
FOR SELECT USING (auth.uid() = id);

-- Policy: Les utilisateurs peuvent mettre à jour leur propre profil
CREATE POLICY "Users can update own profile" ON profiles
FOR UPDATE USING (auth.uid() = id);

-- Policy: Les utilisateurs peuvent insérer leur propre profil (création automatique)
CREATE POLICY "Users can insert own profile" ON profiles
FOR INSERT WITH CHECK (auth.uid() = id);

-- Policy: Les admins peuvent voir tous les profils
CREATE POLICY "Admins can view all profiles" ON profiles
FOR SELECT USING (
  EXISTS (
    SELECT 1 FROM profiles 
    WHERE profiles.id = auth.uid() 
    AND profiles.role = 'ADMIN'
  )
);

-- Policy: Les admins peuvent mettre à jour tous les profils
CREATE POLICY "Admins can update all profiles" ON profiles
FOR UPDATE USING (
  EXISTS (
    SELECT 1 FROM profiles 
    WHERE profiles.id = auth.uid() 
    AND profiles.role = 'ADMIN'
  )
);

-- =====================================================
-- TABLE PRODUCTS
-- =====================================================

-- Policy: Tout le monde peut voir les produits disponibles
CREATE POLICY "Anyone can view available products" ON products
FOR SELECT USING (available = true);

-- Policy: Les agriculteurs peuvent voir leurs propres produits
CREATE POLICY "Farmers can view own products" ON products
FOR SELECT USING (
  farmer_id = auth.uid()
);

-- Policy: Les agriculteurs peuvent insérer leurs propres produits
CREATE POLICY "Farmers can insert own products" ON products
FOR INSERT WITH CHECK (
  farmer_id = auth.uid() AND
  EXISTS (
    SELECT 1 FROM profiles 
    WHERE profiles.id = auth.uid() 
    AND profiles.role = 'FARMER'
  )
);

-- Policy: Les agriculteurs peuvent mettre à jour leurs propres produits
CREATE POLICY "Farmers can update own products" ON products
FOR UPDATE USING (
  farmer_id = auth.uid()
);

-- Policy: Les agriculteurs peuvent supprimer leurs propres produits
CREATE POLICY "Farmers can delete own products" ON products
FOR DELETE USING (
  farmer_id = auth.uid()
);

-- Policy: Les admins peuvent gérer tous les produits
CREATE POLICY "Admins can manage all products" ON products
FOR ALL USING (
  EXISTS (
    SELECT 1 FROM profiles 
    WHERE profiles.id = auth.uid() 
    AND profiles.role = 'ADMIN'
  )
);

-- =====================================================
-- TABLE ORDERS
-- =====================================================

-- Policy: Les clients peuvent voir leurs propres commandes
CREATE POLICY "Customers can view own orders" ON orders
FOR SELECT USING (customer_id = auth.uid());

-- Policy: Les agriculteurs peuvent voir les commandes de leurs produits
CREATE POLICY "Farmers can view product orders" ON orders
FOR SELECT USING (
  farmer_id = auth.uid() AND
  EXISTS (
    SELECT 1 FROM profiles 
    WHERE profiles.id = auth.uid() 
    AND profiles.role = 'FARMER'
  )
);

-- Policy: Les clients peuvent créer des commandes
CREATE POLICY "Customers can create orders" ON orders
FOR INSERT WITH CHECK (
  customer_id = auth.uid() AND
  EXISTS (
    SELECT 1 FROM profiles 
    WHERE profiles.id = auth.uid() 
    AND profiles.role IN ('CITIZEN', 'RESTAURANT')
  ) AND
  -- Vérifier que le produit existe et est disponible
  EXISTS (
    SELECT 1 FROM products 
    WHERE products.id = product_id 
    AND products.available = true
  )
);

-- Policy: Les agriculteurs peuvent mettre à jour le statut de leurs commandes
CREATE POLICY "Farmers can update order status" ON orders
FOR UPDATE USING (
  farmer_id = auth.uid() AND
  EXISTS (
    SELECT 1 FROM profiles 
    WHERE profiles.id = auth.uid() 
    AND profiles.role = 'FARMER'
  )
);

-- Policy: Les clients peuvent annuler leurs propres commandes
CREATE POLICY "Customers can cancel own orders" ON orders
FOR UPDATE USING (
  customer_id = auth.uid() AND
  status IN ('PENDING', 'CONFIRMED')
);

-- Policy: Les admins peuvent gérer toutes les commandes
CREATE POLICY "Admins can manage all orders" ON orders
FOR ALL USING (
  EXISTS (
    SELECT 1 FROM profiles 
    WHERE profiles.id = auth.uid() 
    AND profiles.role = 'ADMIN'
  )
);

-- =====================================================
-- TRIGGERS ET FONCTIONS
-- =====================================================

-- Fonction pour créer automatiquement un profil lors de l'inscription
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.profiles (id, email, full_name, role)
  VALUES (
    NEW.id,
    NEW.email,
    COALESCE(NEW.raw_user_meta_data->>'full_name', 'Utilisateur'),
    COALESCE(NEW.raw_user_meta_data->>'role', 'CITIZEN')::user_role
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger pour créer le profil automatiquement
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- =====================================================
-- VUES SÉCURISÉES
-- =====================================================

-- Vue pour les produits avec informations du vendeur
CREATE OR REPLACE VIEW public.product_details AS
SELECT 
  p.*,
  pr.full_name as farmer_name,
  pr.avatar_url as farmer_avatar,
  pr.phone as farmer_phone
FROM products p
JOIN profiles pr ON p.farmer_id = pr.id
WHERE p.available = true;

-- Policy pour la vue sécurisée
ALTER VIEW product_details OWNER TO postgres;
GRANT SELECT ON public.product_details TO authenticated;
GRANT SELECT ON public.product_details TO anon;

-- =====================================================
-- INDEX DE PERFORMANCE
-- =====================================================

-- Index pour les requêtes fréquentes
CREATE INDEX IF NOT EXISTS idx_profiles_role ON profiles(role);
CREATE INDEX IF NOT EXISTS idx_products_farmer_id ON products(farmer_id);
CREATE INDEX IF NOT EXISTS idx_products_available ON products(available) WHERE available = true;
CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_farmer_id ON orders(farmer_id);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);

-- =====================================================
-- VALIDATIONS ET CONTRAINTES
-- =====================================================

-- Contrainte pour s'assurer que les rôles sont valides
ALTER TABLE profiles 
ADD CONSTRAINT valid_role 
CHECK (role IN ('CITIZEN', 'FARMER', 'RESTAURANT', 'ADMIN'));

-- Contrainte pour les prix positifs
ALTER TABLE products 
ADD CONSTRAINT positive_price 
CHECK (price > 0);

-- Contrainte pour les quantités positives
ALTER TABLE products 
ADD CONSTRAINT positive_quantity 
CHECK (quantity >= 0);

-- Contrainte pour les statuts de commande valides
ALTER TABLE orders 
ADD CONSTRAINT valid_status 
CHECK (status IN ('PENDING', 'CONFIRMED', 'SHIPPED', 'DELIVERED', 'CANCELLED'));

-- =====================================================
-- FONCTIONS D'AUDIT
-- =====================================================

-- Fonction pour logger les actions sensibles
CREATE OR REPLACE FUNCTION public.log_sensitive_action(
  action_type TEXT,
  table_name TEXT,
  record_id TEXT,
  details JSONB DEFAULT '{}'::jsonb
)
RETURNS VOID AS $$
BEGIN
  INSERT INTO audit_logs (user_id, action_type, table_name, record_id, details, created_at)
  VALUES (
    auth.uid(),
    action_type,
    table_name,
    record_id,
    details,
    NOW()
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Table d'audit (si elle n'existe pas déjà)
CREATE TABLE IF NOT EXISTS public.audit_logs (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id),
  action_type TEXT NOT NULL,
  table_name TEXT NOT NULL,
  record_id TEXT,
  details JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Activer RLS sur la table d'audit
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

-- Policies pour la table d'audit
CREATE POLICY "Users can view own audit logs" ON audit_logs
FOR SELECT USING (user_id = auth.uid());

CREATE POLICY "Admins can view all audit logs" ON audit_logs
FOR SELECT USING (
  EXISTS (
    SELECT 1 FROM profiles 
    WHERE profiles.id = auth.uid() 
    AND profiles.role = 'ADMIN'
  )
);

-- =====================================================
-- SÉCURITÉ ACCÉS BASE DE DONNÉES
-- =====================================================

-- Révoquer les accès par défaut
REVOKE ALL ON SCHEMA public FROM anon;
REVOKE ALL ON SCHEMA public FROM authenticated;

-- Donner les accès minimaux nécessaires
GRANT USAGE ON SCHEMA public TO anon;
GRANT USAGE ON SCHEMA public TO authenticated;

-- Accès anonymes (lecture seule sur les données publiques)
GRANT SELECT ON public.product_details TO anon;
GRANT SELECT (id, email, created_at) ON public.profiles TO anon;

-- Accès authentifiés
GRANT SELECT ON public.product_details TO authenticated;
GRANT SELECT ON public.profiles TO authenticated;
GRANT SELECT ON public.products TO authenticated;
GRANT SELECT ON public.orders TO authenticated;
GRANT INSERT ON public.profiles TO authenticated;
GRANT UPDATE ON public.profiles TO authenticated;
GRANT INSERT ON public.products TO authenticated;
GRANT UPDATE ON public.products TO authenticated;
GRANT DELETE ON public.products TO authenticated;
GRANT INSERT ON public.orders TO authenticated;
GRANT UPDATE ON public.orders TO authenticated;

-- Accès admin complet
GRANT ALL ON ALL TABLES IN SCHEMA public TO authenticated;
