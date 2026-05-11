-- =====================================================
-- VITACHAIN INITIAL SCHEMA
-- Migration initiale pour la base de données Supabase
-- =====================================================

-- Types personnalisés
CREATE TYPE user_role AS ENUM ('CITIZEN', 'FARMER', 'RESTAURANT', 'ADMIN');
CREATE TYPE order_status AS ENUM ('PENDING', 'CONFIRMED', 'SHIPPED', 'DELIVERED', 'CANCELLED');

-- =====================================================
-- TABLE PROFILES
-- Extension de la table auth.users avec des métadonnées
-- =====================================================

CREATE TABLE IF NOT EXISTS public.profiles (
  id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
  email TEXT NOT NULL,
  full_name TEXT,
  role user_role NOT NULL DEFAULT 'CITIZEN',
  avatar_url TEXT,
  phone TEXT,
  address TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  email_verified BOOLEAN DEFAULT FALSE,
  last_sign_in_at TIMESTAMP WITH TIME ZONE,
  
  CONSTRAINT profiles_email_unique UNIQUE (email),
  CONSTRAINT profiles_role_valid CHECK (role IN ('CITIZEN', 'FARMER', 'RESTAURANT', 'ADMIN'))
);

-- =====================================================
-- TABLE PRODUCTS
-- Produits des agriculteurs
-- =====================================================

CREATE TABLE IF NOT EXISTS public.products (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  name TEXT NOT NULL,
  description TEXT,
  price DECIMAL(10,2) NOT NULL,
  category TEXT NOT NULL,
  farmer_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE NOT NULL,
  available BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  images TEXT[] DEFAULT '{}',
  location TEXT,
  organic BOOLEAN DEFAULT FALSE,
  quantity DECIMAL(10,2) NOT NULL DEFAULT 0,
  unit TEXT NOT NULL DEFAULT 'kg',
  
  CONSTRAINT products_price_positive CHECK (price > 0),
  CONSTRAINT products_quantity_positive CHECK (quantity >= 0)
);

-- =====================================================
-- TABLE ORDERS
-- Commandes des clients
-- =====================================================

CREATE TABLE IF NOT EXISTS public.orders (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  customer_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE NOT NULL,
  farmer_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE NOT NULL,
  product_id UUID REFERENCES public.products(id) ON DELETE CASCADE NOT NULL,
  quantity DECIMAL(10,2) NOT NULL,
  total_price DECIMAL(10,2) NOT NULL,
  status order_status DEFAULT 'PENDING',
  delivery_address TEXT,
  delivery_notes TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  
  CONSTRAINT orders_quantity_positive CHECK (quantity > 0),
  CONSTRAINT orders_total_price_positive CHECK (total_price > 0),
  CONSTRAINT orders_status_valid CHECK (status IN ('PENDING', 'CONFIRMED', 'SHIPPED', 'DELIVERED', 'CANCELLED'))
);

-- =====================================================
-- TABLE AUDIT LOGS
-- Pour traçabilité des actions sensibles
-- =====================================================

CREATE TABLE IF NOT EXISTS public.audit_logs (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
  action_type TEXT NOT NULL,
  table_name TEXT NOT NULL,
  record_id TEXT,
  details JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- TABLE NOTIFICATIONS
-- Système de notifications
-- =====================================================

CREATE TABLE IF NOT EXISTS public.notifications (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE NOT NULL,
  title TEXT NOT NULL,
  message TEXT NOT NULL,
  type TEXT NOT NULL DEFAULT 'info',
  read BOOLEAN DEFAULT FALSE,
  data JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  expires_at TIMESTAMP WITH TIME ZONE
);

-- =====================================================
-- TABLE FARMER_STATS
-- Statistiques pour les agriculteurs
-- =====================================================

CREATE TABLE IF NOT EXISTS public.farmer_stats (
  id UUID REFERENCES public.profiles(id) ON DELETE CASCADE PRIMARY KEY,
  total_products INTEGER DEFAULT 0,
  total_orders INTEGER DEFAULT 0,
  total_revenue DECIMAL(15,2) DEFAULT 0,
  average_rating DECIMAL(3,2) DEFAULT 0,
  last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  
  CONSTRAINT farmer_stats_non_negative CHECK (
    total_products >= 0 AND 
    total_orders >= 0 AND 
    total_revenue >= 0 AND 
    average_rating >= 0 AND 
    average_rating <= 5
  )
);

-- =====================================================
-- TRIGGERS AUTOMATIQUES
-- =====================================================

-- Trigger pour mettre à jour updated_at
CREATE OR REPLACE FUNCTION public.set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Appliquer le trigger sur les tables pertinentes
CREATE TRIGGER set_profiles_updated_at 
  BEFORE UPDATE ON public.profiles 
  FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

CREATE TRIGGER set_products_updated_at 
  BEFORE UPDATE ON public.products 
  FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

CREATE TRIGGER set_orders_updated_at 
  BEFORE UPDATE ON public.orders 
  FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

-- =====================================================
-- VUES UTILITAIRES
-- =====================================================

-- Vue pour les produits avec informations complètes
CREATE OR REPLACE VIEW public.product_list AS
SELECT 
  p.*,
  pr.full_name as farmer_name,
  pr.avatar_url as farmer_avatar,
  pr.phone as farmer_phone,
  pr.location as farmer_location
FROM products p
JOIN profiles pr ON p.farmer_id = pr.id
WHERE p.available = true;

-- Vue pour les commandes avec détails
CREATE OR REPLACE VIEW public.order_details AS
SELECT 
  o.*,
  p.name as product_name,
  p.images as product_images,
  c.full_name as customer_name,
  c.email as customer_email,
  f.full_name as farmer_name,
  f.email as farmer_email
FROM orders o
JOIN products p ON o.product_id = p.id
JOIN profiles c ON o.customer_id = c.id
JOIN profiles f ON o.farmer_id = f.id;

-- =====================================================
-- INDEX DE PERFORMANCE
-- =====================================================

-- Index pour les performances
CREATE INDEX IF NOT EXISTS idx_profiles_email ON public.profiles(email);
CREATE INDEX IF NOT EXISTS idx_profiles_role ON public.profiles(role);
CREATE INDEX IF NOT EXISTS idx_products_farmer_id ON public.products(farmer_id);
CREATE INDEX IF NOT EXISTS idx_products_category ON public.products(category);
CREATE INDEX IF NOT EXISTS idx_products_available ON public.products(available) WHERE available = true;
CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON public.orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_farmer_id ON public.orders(farmer_id);
CREATE INDEX IF NOT EXISTS idx_orders_status ON public.orders(status);
CREATE INDEX IF NOT EXISTS idx_orders_created_at ON public.orders(created_at);
CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON public.notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_read ON public.notifications(read) WHERE read = FALSE;
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON public.audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON public.audit_logs(created_at);

-- =====================================================
-- FONCTIONS UTILITAIRES
-- =====================================================

-- Fonction pour calculer les statistiques d'un agriculteur
CREATE OR REPLACE FUNCTION public.update_farmer_stats(farmer_uuid UUID)
RETURNS VOID AS $$
DECLARE
  total_products INTEGER;
  total_orders INTEGER;
  total_revenue DECIMAL(15,2);
  avg_rating DECIMAL(3,2);
BEGIN
  -- Compter les produits actifs
  SELECT COUNT(*) INTO total_products
  FROM products
  WHERE farmer_id = farmer_uuid AND available = TRUE;
  
  -- Compter les commandes confirmées ou livrées
  SELECT COUNT(*) INTO total_orders
  FROM orders
  WHERE farmer_id = farmer_uuid AND status IN ('CONFIRMED', 'SHIPPED', 'DELIVERED');
  
  -- Calculer le revenu total
  SELECT COALESCE(SUM(total_price), 0) INTO total_revenue
  FROM orders
  WHERE farmer_id = farmer_uuid AND status IN ('DELIVERED');
  
  -- Calculer la note moyenne (placeholder pour l'instant)
  SELECT 0.0 INTO avg_rating;
  
  -- Mettre à jour ou insérer les statistiques
  INSERT INTO farmer_stats (id, total_products, total_orders, total_revenue, average_rating, last_updated)
  VALUES (farmer_uuid, total_products, total_orders, total_revenue, avg_rating, NOW())
  ON CONFLICT (id) DO UPDATE SET
    total_products = EXCLUDED.total_products,
    total_orders = EXCLUDED.total_orders,
    total_revenue = EXCLUDED.total_revenue,
    average_rating = EXCLUDED.average_rating,
    last_updated = NOW();
END;
$$ LANGUAGE plpgsql;

-- Trigger pour mettre à jour les statistiques automatiquement
CREATE OR REPLACE FUNCTION public.update_stats_on_change()
RETURNS TRIGGER AS $$
BEGIN
  IF TG_TABLE_NAME = 'products' THEN
    PERFORM public.update_farmer_stats(NEW.farmer_id);
  ELSIF TG_TABLE_NAME = 'orders' THEN
    PERFORM public.update_farmer_stats(NEW.farmer_id);
  END IF;
  RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- Appliquer les triggers de statistiques
CREATE TRIGGER update_stats_on_product_change
  AFTER INSERT OR UPDATE OR DELETE ON public.products
  FOR EACH ROW EXECUTE FUNCTION public.update_stats_on_change();

CREATE TRIGGER update_stats_on_order_change
  AFTER INSERT OR UPDATE ON public.orders
  FOR EACH ROW EXECUTE FUNCTION public.update_stats_on_change();

-- =====================================================
-- DONNÉES INITIALES (optionnel pour le développement)
-- =====================================================

-- Créer un utilisateur admin par défaut (commenté en production)
-- INSERT INTO public.profiles (id, email, full_name, role, email_verified)
-- VALUES (
--   gen_random_uuid(),
--   'admin@vitachain.ma',
--   'Admin VitaChain',
--   'ADMIN',
--   TRUE
-- );

-- =====================================================
-- COMMENTAIRES
-- =====================================================

COMMENT ON TABLE public.profiles IS 'Profils utilisateurs étendant auth.users';
COMMENT ON TABLE public.products IS 'Produits proposés par les agriculteurs';
COMMENT ON TABLE public.orders IS 'Commandes passées par les clients';
COMMENT ON TABLE public.audit_logs IS 'Journal d\'audit pour la traçabilité';
COMMENT ON TABLE public.notifications IS 'Notifications système pour les utilisateurs';
COMMENT ON TABLE public.farmer_stats IS 'Statistiques calculées pour les agriculteurs';
