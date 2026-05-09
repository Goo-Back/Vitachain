# Product Requirements Document (PRD)
# VITACHAIN v2.0 — Plateforme Agri-Alimentaire Marocaine

---

## Document Metadata

| Field | Value |
|---|---|
| **Project** | VitaChain v1.0 |
| **Author** | Yasser |
| **Version** | 1.0 — MVD (Minimum Viable Deployment) |
| **Date** | 2026-04-24 |
| **Status** | Approved for Development |
| **Timeline** | 8 semaines |
| **Budget OPEX** | ~110 MAD/mois |

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Problem Statement](#2-problem-statement)
3. [Product Vision & Goals](#3-product-vision--goals)
4. [Users & Personas](#4-users--personas)
5. [Functional Requirements](#5-functional-requirements)
6. [Non-Functional Requirements](#6-non-functional-requirements)
7. [Technical Architecture](#7-technical-architecture)
8. [Data Models](#8-data-models)
9. [API Contracts](#9-api-contracts)
10. [Module Specifications](#10-module-specifications)
11. [External Integrations](#11-external-integrations)
12. [Security Requirements](#12-security-requirements)
13. [MVP Scope & Exclusions](#13-mvp-scope--exclusions)
14. [Implementation Timeline](#14-implementation-timeline)
15. [Success Metrics](#15-success-metrics)
16. [Risks & Mitigations](#16-risks--mitigations)

---

## 1. Executive Summary

Vitachain est une plateforme web marocaine qui connecte l'agriculture intelligente, la distribution alimentaire B2B, et la réduction du gaspillage alimentaire en restauration. Elle est construite autour de 4 modules métier complémentaires :

- **KATARA** — Smart farming IoT avec analyse IA agronomique
- **FARMARKET** — Marketplace B2B produits agricoles
- **BOTABA9A** — Vitrine marketing IoT pour la restauration
- **SECONDSERVE** — Click & Collect repas invendus

La plateforme cible le marché marocain et est optimisée pour les connexions 3G des zones rurales.

---

## 2. Problem Statement

### 2.1 Problèmes Identifiés

**Agriculture marocaine :**
- Les petits agriculteurs n'ont pas accès à des outils de surveillance de leurs cultures en temps réel
- Aucune alerte automatique sur les conditions critiques (chaleur excessive, sécheresse)
- Pas d'analyse agronomique accessible et abordable

**Commerce B2B agricole :**
- La mise en relation producteurs/acheteurs reste informelle (téléphone, intermédiaires)
- Pas de plateforme numérique centralisée pour les produits agricoles marocains
- Manque de transparence sur les prix et disponibilités

**Gaspillage alimentaire en restauration :**
- Les restaurants marocains jettent chaque soir une quantité significative de repas invendus
- Aucune solution numérique locale pour connecter les surplus avec les citoyens
- Problème environnemental et économique non adressé

### 2.2 Opportunité de Marché

- +1.5 million d'agriculteurs au Maroc
- Secteur HoReCa en croissance avec digitalisation accélérée post-COVID
- Pas de concurrent direct sur le segment IoT agricole + marketplace intégré au Maroc

---

## 3. Product Vision & Goals

### 3.1 Vision

> Vitachain est le système nerveux numérique de la chaîne agri-alimentaire marocaine — de la graine jusqu'à l'assiette.

### 3.2 Objectifs MVD (8 semaines)

| Priorité | Objectif | Indicateur |
|---|---|---|
| P0 | Infrastructure opérationnelle | VPS + Docker + NGINX + Supabase déployés |
| P0 | Auth multi-rôles fonctionnelle | Inscription/connexion pour 4 rôles |
| P1 | KATARA MVP | Ingestion ESP32 + Dashboard + 1 analyse IA |
| P1 | FARMARKET MVP | CRUD annonces + recherche publique |
| P1 | SECONDSERVE MVP | Création repas + réservation + email |
| P2 | BOTABA9A | Vitrine statique + formulaire lead |

### 3.3 Objectifs Post-MVD (V2)

- Paiements intégrés (CIB, PayPal)
- Application mobile React Native
- Tableau de bord administrateur avancé
- Support multilingue (Arabe, Français, Anglais)
- Imagerie satellite NDVI (Sentinel Hub)

---

## 4. Users & Personas

### 4.1 FARMER — L'Agriculteur

**Profil :** Agriculteur marocain, 30-60 ans, exploitant de 2 à 50 hectares. Souvent en zone rurale, connexion 3G limitée. Niveau tech : faible à moyen.

**Besoins :**
- Voir l'état de ses cultures en temps réel depuis son téléphone
- Recevoir des alertes quand quelque chose ne va pas
- Vendre ses produits directement sans intermédiaire
- Obtenir des conseils agronomiques adaptés au Maroc

**Jobs to be done :**
- "Je veux savoir si mes parcelles ont besoin d'eau ce soir"
- "Je veux vendre mes tomates directement à un restaurant de Casablanca"
- "Je veux comprendre pourquoi mon NDVI a baissé cette semaine"

**Contraintes :** Interface simple, mobile-first, texte lisible, chargement rapide en 3G.

---

### 4.2 RESTAURANT — Le Restaurateur

**Profil :** Gérant d'un restaurant à Casablanca, Rabat, Marrakech. 25-50 ans, digitalement actif. Gère une équipe de 5-20 personnes.

**Besoins :**
- Acheter des produits agricoles frais en direct des producteurs
- Réduire les pertes sur les repas non vendus en fin de service
- Gérer les retraits physiques de commandes SecondServe
- Accéder à des équipements IoT intelligents (Botaba9a)

**Jobs to be done :**
- "Je veux vendre mes 20 tajines invendus ce soir à prix réduit"
- "Je veux trouver des tomates certifiées bio directement d'un agriculteur"
- "Je veux valider facilement les retraits des clients"

---

### 4.3 CITIZEN — Le Citoyen

**Profil :** Habitant urbain, 20-45 ans, sensible au gaspillage alimentaire ou simplement à la recherche de bons repas à prix réduit. Digitalement actif, smartphone Android/iOS.

**Besoins :**
- Trouver des repas disponibles près de chez lui à prix réduit
- Réserver et récupérer facilement
- Savoir son code de retrait pour le restaurant

**Jobs to be done :**
- "Je veux trouver un repas complet à 30 DH ce soir dans mon quartier"
- "Je veux recevoir une confirmation par email avec mon code de retrait"

---

### 4.4 ADMIN — L'Administrateur Plateforme

**Profil :** Équipe Vitachain. Accès complet à toutes les données.

**Besoins :**
- Surveiller la santé technique de la plateforme
- Gérer les utilisateurs (approbation, blocage)
- Voir les statistiques d'utilisation
- Accéder aux logs d'audit

---

### 4.5 SUPPORT — Agent Support Client

**Profil :** Équipe support Vitachain. Accès en lecture aux données utilisateurs.

**Besoins :**
- Résoudre les problèmes de réservation (code perdu, annulation tardive)
- Débloquer des comptes
- Accéder à l'historique d'un utilisateur

---

## 5. Functional Requirements

### 5.1 User Management & Authentication (FR01–FR10)

| ID | Requirement | Priorité | Module |
|---|---|---|---|
| FR01 | Inscription utilisateur avec email + vérification | P0 | Auth |
| FR02 | Connexion email/mot de passe avec JWT httpOnly | P0 | Auth |
| FR03 | Magic link authentication | P2 | Auth |
| FR04 | Réinitialisation mot de passe par email | P1 | Auth |
| FR05 | Gestion profil (nom, téléphone, rôle) | P1 | Auth |
| FR06 | Contrôle accès basé sur les rôles (RBAC) | P0 | Auth |
| FR07 | Tableau de bord gestion utilisateurs (admin) | P2 | Admin |
| FR08 | Détection connexions suspectes | P2 | Auth |
| FR09 | Blocage temporaire de compte | P2 | Auth |
| FR10 | Déconnexion + invalidation session | P1 | Auth |

### 5.2 KATARA Smart Farming (FR11–FR21)

| ID | Requirement | Priorité | Module |
|---|---|---|---|
| FR11 | Enregistrement device IoT ESP32 | P0 | KATARA |
| FR12 | Ingestion données télémétrie ESP32 (<50ms) | P0 | KATARA |
| FR13 | Visualisation temps réel dashboard | P0 | KATARA |
| FR14 | Historique télémétrie avec analyse de tendances | P1 | KATARA |
| FR15 | Recommandations IA agronomiques (Claude API) | P1 | KATARA |
| FR16 | Intégration données météo (OpenWeatherMap) | P1 | KATARA |
| FR17 | Imagerie satellite NDVI (Sentinel Hub) | P2 | KATARA |
| FR18 | Système d'alertes conditions critiques | P0 | KATARA |
| FR19 | Gestion alertes lu/non-lu | P1 | KATARA |
| FR20 | Génération automatique recommandations IA | P1 | KATARA |
| FR21 | Déclenchement alertes sur dépassement seuil | P0 | KATARA |

**Seuils d'alerte automatique :**
- Température > 40°C → `severity: high`
- Humidité < 20% → `severity: high`
- NDVI < 0.3 → `severity: medium` (stress végétation)

### 5.3 FARMARKET B2B Marketplace (FR22–FR32)

| ID | Requirement | Priorité | Module |
|---|---|---|---|
| FR22 | Création annonce produit agricole | P0 | FARMARKET |
| FR23 | Modification et suppression annonce | P0 | FARMARKET |
| FR24 | Navigation publique des annonces | P0 | FARMARKET |
| FR25 | Recherche géolocalisée (OpenStreetMap) | P2 | FARMARKET |
| FR26 | Filtres : produit, localisation, prix | P1 | FARMARKET |
| FR27 | Passation commande B2B | P1 | FARMARKET |
| FR28 | Historique et statut commandes (acheteur) | P1 | FARMARKET |
| FR29 | Annulation commande en attente | P1 | FARMARKET |
| FR30 | Vue commandes reçues (farmer) | P1 | FARMARKET |
| FR31 | Confirmation/annulation commande (farmer) | P1 | FARMARKET |
| FR32 | Suivi statut commande | P1 | FARMARKET |

**Règle critique FARMARKET :** `farmer_id` est TOUJOURS injecté depuis le JWT. Jamais accepté depuis le request body.

### 5.4 SECONDSERVE B2C Marketplace (FR33–FR45)

| ID | Requirement | Priorité | Module |
|---|---|---|---|
| FR33 | Création annonce repas (restaurant) | P0 | SECONDSERVE |
| FR34 | Définition créneau de retrait | P0 | SECONDSERVE |
| FR35 | Modification et suppression annonce repas | P1 | SECONDSERVE |
| FR36 | Vue réservations pour restaurants | P1 | SECONDSERVE |
| FR37 | Validation code de retrait physique | P0 | SECONDSERVE |
| FR38 | Navigation repas disponibles (citoyen) | P0 | SECONDSERVE |
| FR39 | Recherche par localisation/prix/cuisine | P1 | SECONDSERVE |
| FR40 | Réservation repas (atomique, sans double booking) | P0 | SECONDSERVE |
| FR41 | Historique réservations (citoyen) | P1 | SECONDSERVE |
| FR42 | Annulation réservation (>2h avant pickup) | P1 | SECONDSERVE |
| FR43 | Génération code retrait unique (6 chiffres) | P0 | SECONDSERVE |
| FR44 | Expiration automatique annonce repas | P1 | SECONDSERVE |
| FR45 | Expiration automatique créneaux réservation | P1 | SECONDSERVE |

**Règle critique SECONDSERVE :** La réservation utilise une RPC Supabase transactionnelle pour éviter le double booking. Le code de retrait est généré côté serveur (jamais côté client).

### 5.5 BOTABA9A Marketing (FR46–FR49)

| ID | Requirement | Priorité | Module |
|---|---|---|---|
| FR46 | Pages marketing statiques (SSG) | P0 | BOTABA9A |
| FR47 | Formulaire de contact lead | P0 | BOTABA9A |
| FR48 | Capture et stockage lead (botaba9a_leads) | P0 | BOTABA9A |
| FR49 | Affichage fiches produits IoT | P1 | BOTABA9A |

### 5.6 Platform Administration (FR50–FR57)

| ID | Requirement | Priorité | Module |
|---|---|---|---|
| FR50 | Dashboard métriques santé système | P2 | Admin |
| FR51 | Monitoring statut capteurs IoT | P2 | Admin |
| FR52 | Approbation inscription utilisateurs | P2 | Admin |
| FR53 | Statistiques d'utilisation plateforme | P2 | Admin |
| FR54 | Détection et blocage comportements abusifs | P2 | Admin |
| FR55 | Consultation journaux d'audit | P2 | Admin |
| FR56 | Métriques et alertes performance | P2 | Admin |
| FR57 | Détection anomalies trafic API / capteurs | P2 | Admin |

### 5.7 Customer Support (FR58–FR64)

| ID | Requirement | Priorité | Module |
|---|---|---|---|
| FR58 | Gestion tickets support | P2 | Support |
| FR59 | Vue informations compte utilisateur | P2 | Support |
| FR60 | Libération blocage sécurité | P2 | Support |
| FR61 | Réinitialisation code de retrait | P2 | Support |
| FR62 | Accès base de connaissances | P2 | Support |
| FR63 | Soumission demande support (utilisateur) | P2 | Support |
| FR64 | Suivi statut ticket | P2 | Support |

### 5.8 Notifications & Communication (FR65–FR70)

| ID | Requirement | Priorité | Module |
|---|---|---|---|
| FR65 | Emails notifications alertes KATARA | P1 | Notifications |
| FR66 | Emails notifications commandes FARMARKET | P1 | Notifications |
| FR67 | Emails confirmations réservations SECONDSERVE | P0 | Notifications |
| FR68 | Emails confirmation code de retrait | P0 | Notifications |
| FR69 | Emails notifications leads BOTABA9A | P1 | Notifications |
| FR70 | Notifications in-app temps réel | P1 | Notifications |

---

## 6. Non-Functional Requirements

### 6.1 Performance

| Métrique | Cible | Commentaire |
|---|---|---|
| Ingestion télémétrie IoT | < 50ms | ESP32 → Supabase via FastAPI |
| Réponse API REST | < 200ms | P95, hors appels Claude |
| Chargement pages publiques | < 2.5s | Connexion 4G |
| Chargement dashboards | < 3.0s | Connexion 4G |
| Mises à jour temps réel | < 2s | Supabase Realtime WebSocket |
| Appels Claude API | < 30s | Timeout configuré |

### 6.2 Scalabilité

- Support de 10 à 1 000 utilisateurs actifs simultanés
- Croissance 10x avec < 10% de dégradation de performance
- Architecture permettant l'extraction vers VPS séparés (Phase 2)
- Insertion télémétrie : jusqu'à 1 000 lectures/minute

### 6.3 Disponibilité & Fiabilité

- **Uptime cible :** 99.9% (< 8.7h de downtime/an)
- **Zero data loss** pour les données de télémétrie
- **RTO (Recovery Time Objective) :** 4 heures
- **RPO (Recovery Point Objective) :** 15 minutes
- Backups automatiques quotidiens Supabase (rétention 30 jours)

### 6.4 Sécurité

- Chiffrement en transit : HTTPS/TLS 1.3 (Let's Encrypt)
- Chiffrement au repos : PostgreSQL Supabase (géré)
- Authentification : JWT Supabase, expiry 24h, refresh 30 jours
- Autorisation : RLS au niveau base de données
- API Key IoT : rotation tous les 90 jours
- Conformité GDPR : suppression données sur demande
- Jamais de clé secrète dans le code source ou Git

### 6.5 Accessibilité

- WCAG 2.1 niveau AA
- Support RTL pour l'arabe (post-MVD)
- Mobile-first design
- Optimisation 3G pour les zones rurales

### 6.6 Compatibilité

- Navigateurs modernes uniquement (Chrome 90+, Firefox 90+, Safari 14+)
- Pas de support IE11
- Responsive : 320px → 1920px
- PWA-ready (post-MVD)

---

## 7. Technical Architecture

### 7.1 Vue d'ensemble

```
Internet
    │
    ▼
┌─────────────────────────────────────────────────┐
│  NGINX (Docker)  — vitachain.ma / api.vitachain.ma  │
│  Ports: 80 (→443), 443 (SSL Let's Encrypt)        │
│  Rate limiting · CORS · Gzip · Security headers   │
└──────────┬──────────────────────┬────────────────┘
           │                      │
           ▼                      ▼
    ┌─────────────┐       ┌───────────────────────────────────┐
    │  Frontend   │       │          Backend FastAPI           │
    │  Next.js 14 │       │                                   │
    │  TypeScript │       │  /api/telemetry  → port 8000      │
    │  Port 3000  │       │  /api/katara/    → port 8000      │
    │  (interne)  │       │  /api/farmarket/ → port 8001      │
    └──────┬──────┘       │  /api/secondserve/ → port 8002    │
           │              └──────────────┬────────────────────┘
           │                             │
           └──────────────┬──────────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │   Supabase Cloud      │
              │   PostgreSQL + Auth   │
              │   + Realtime + RLS    │
              └───────────────────────┘
```

### 7.2 Stack Technique

| Composant | Technologie | Version | Port |
|---|---|---|---|
| Gateway | NGINX | alpine | 80/443 |
| Frontend | Next.js + TypeScript | 14.x | 3000 |
| Backend | FastAPI + Python | 0.110+ / 3.11 | 8000/8001/8002 |
| Base de données | Supabase PostgreSQL | Cloud | Cloud |
| Authentification | Supabase Auth | v2 | Cloud |
| Temps réel | Supabase Realtime | v2 | Cloud |
| Conteneurisation | Docker + Compose | 24+ / v2 | — |
| Infrastructure | DigitalOcean VPS | Ubuntu 24.04 | — |
| CSS | Tailwind CSS | 3.x | — |
| Validation Python | Pydantic | v2 | — |
| Client Supabase Python | supabase-py | 2.3+ | — |
| Client Supabase JS | @supabase/supabase-js | v2 | — |
| HTTP async Python | httpx | 0.27+ | — |

### 7.3 Règles Architecture Critiques

```
❌ JAMAIS                              ✅ TOUJOURS
─────────────────────────────────────────────────────
SQLAlchemy / ORM                   supabase-py 2.x
JWT custom maison                  Supabase Auth JWT
ports: 8000:8000 dans compose      expose: ['8000']
anthropic.Anthropic() sync         anthropic.AsyncAnthropic()
requests.get()                     httpx.AsyncClient()
farmer_id depuis le body           farmer_id depuis JWT.sub
SDK Brevo                          httpx POST api.brevo.com
clé dans le code source            variables .env
```

### 7.4 Réseau Docker

```yaml
# Réseau interne — tous les services se voient par nom
networks:
  vitachain_network:
    driver: bridge

# Seul NGINX est exposé
nginx:
  ports: ['80:80', '443:443']  # ← seul service avec ports:

frontend:
  expose: ['3000']  # ← visible uniquement en interne

backend (M1/M2/M4):
  expose: ['8000']  # ← jamais ports:, jamais sur Internet
```

### 7.5 Authentification Flow

```
1. Utilisateur soumet email + password
2. Frontend → Supabase Auth signInWithPassword()
3. Supabase retourne JWT (access_token)
4. Frontend stocke JWT dans cookie httpOnly via @supabase/ssr
5. Sur requête backend protégée :
   Frontend → NGINX → Backend FastAPI
   Backend extrait JWT depuis Authorization: Bearer header
   Backend decode avec python-jose + SUPABASE_JWT_SECRET
   Backend lit role depuis payload.user_metadata.role
6. RLS Supabase vérifie auth.uid() pour chaque requête DB
```

---

## 8. Data Models

### 8.1 Table: profiles

```sql
CREATE TABLE profiles (
  id          UUID REFERENCES auth.users PRIMARY KEY,
  role        TEXT CHECK (role IN ('FARMER','RESTAURANT','CITIZEN','ADMIN','SUPPORT')),
  full_name   TEXT,
  phone       TEXT,
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  updated_at  TIMESTAMPTZ DEFAULT NOW()
);

-- Trigger : création automatique à l'inscription
CREATE OR REPLACE FUNCTION handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO profiles (id, role, full_name)
  VALUES (
    NEW.id,
    NEW.raw_user_meta_data->>'role',
    NEW.raw_user_meta_data->>'full_name'
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION handle_new_user();
```

### 8.2 Table: iot_devices

```sql
CREATE TABLE iot_devices (
  id            UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  device_id     TEXT UNIQUE NOT NULL,      -- 'katara-{uuid4}'
  farmer_id     UUID REFERENCES profiles(id),
  name          TEXT,                       -- 'Parcelle Nord'
  location_lat  FLOAT,
  location_lng  FLOAT,
  registered_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 8.3 Table: telemetry_readings

```sql
CREATE TABLE telemetry_readings (
  id            UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  device_id     TEXT NOT NULL,
  farmer_id     UUID REFERENCES profiles(id),
  temperature   FLOAT CHECK (temperature BETWEEN -10 AND 60),
  humidity      FLOAT CHECK (humidity BETWEEN 0 AND 100),
  ndvi          FLOAT CHECK (ndvi BETWEEN -1 AND 1),
  battery_level FLOAT,
  timestamp     TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_telemetry_device_time
  ON telemetry_readings (device_id, timestamp DESC);

CREATE INDEX idx_telemetry_farmer
  ON telemetry_readings (farmer_id, timestamp DESC);
```

### 8.4 Table: katara_alerts

```sql
CREATE TABLE katara_alerts (
  id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  farmer_id   UUID REFERENCES profiles(id) NOT NULL,
  device_id   TEXT,
  type        TEXT NOT NULL,  -- 'threshold_exceeded' | 'ai_recommendation' | 'weather_risk'
  severity    TEXT CHECK (severity IN ('low','medium','high','critical')),
  message     TEXT NOT NULL,
  is_read     BOOLEAN DEFAULT FALSE,
  created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_alerts_farmer_unread
  ON katara_alerts (farmer_id, is_read, created_at DESC);
```

### 8.5 Table: farm_listings

```sql
CREATE TABLE farm_listings (
  id            UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  farmer_id     UUID REFERENCES profiles(id) NOT NULL,
  title         TEXT NOT NULL CHECK (length(title) <= 100),
  product_type  TEXT NOT NULL,
  quantity_kg   FLOAT CHECK (quantity_kg > 0),
  price_per_kg  FLOAT CHECK (price_per_kg > 0),
  description   TEXT CHECK (length(description) <= 500),
  location_lat  FLOAT,
  location_lng  FLOAT,
  status        TEXT DEFAULT 'active' CHECK (status IN ('active','sold','expired')),
  created_at    TIMESTAMPTZ DEFAULT NOW()
);
```

### 8.6 Table: farm_orders

```sql
CREATE TABLE farm_orders (
  id           UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  listing_id   UUID REFERENCES farm_listings(id) NOT NULL,
  buyer_id     UUID REFERENCES profiles(id) NOT NULL,
  quantity_kg  FLOAT CHECK (quantity_kg > 0),
  total_price  FLOAT,
  status       TEXT DEFAULT 'pending'
               CHECK (status IN ('pending','confirmed','cancelled','delivered')),
  created_at   TIMESTAMPTZ DEFAULT NOW()
);
```

### 8.7 Table: botaba9a_leads

```sql
CREATE TABLE botaba9a_leads (
  id         UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  name       TEXT NOT NULL,
  email      TEXT NOT NULL,
  phone      TEXT,
  message    TEXT,
  source     TEXT DEFAULT 'contact_form',
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 8.8 Table: meal_listings

```sql
CREATE TABLE meal_listings (
  id                 UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  restaurant_id      UUID REFERENCES profiles(id) NOT NULL,
  title              TEXT NOT NULL,
  description        TEXT,
  price              FLOAT CHECK (price > 0),
  quantity_available INT CHECK (quantity_available >= 0),
  pickup_start       TIMESTAMPTZ NOT NULL,
  pickup_end         TIMESTAMPTZ NOT NULL,
  status             TEXT DEFAULT 'available'
                     CHECK (status IN ('available','closed','expired','cancelled')),
  CHECK (pickup_end > pickup_start)
);
```

### 8.9 Table: meal_reservations

```sql
CREATE TABLE meal_reservations (
  id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  meal_id     UUID REFERENCES meal_listings(id) NOT NULL,
  citizen_id  UUID REFERENCES profiles(id) NOT NULL,
  quantity    INT CHECK (quantity > 0),
  pickup_code TEXT UNIQUE NOT NULL,  -- 6 chiffres, UNIQUE
  status      TEXT DEFAULT 'confirmed'
              CHECK (status IN ('confirmed','cancelled','collected','expired')),
  created_at  TIMESTAMPTZ DEFAULT NOW()
);
```

### 8.10 Row Level Security (RLS)

```sql
-- Activer RLS sur toutes les tables
ALTER TABLE profiles          ENABLE ROW LEVEL SECURITY;
ALTER TABLE telemetry_readings ENABLE ROW LEVEL SECURITY;
ALTER TABLE katara_alerts      ENABLE ROW LEVEL SECURITY;
ALTER TABLE farm_listings      ENABLE ROW LEVEL SECURITY;
ALTER TABLE farm_orders        ENABLE ROW LEVEL SECURITY;
ALTER TABLE botaba9a_leads     ENABLE ROW LEVEL SECURITY;
ALTER TABLE meal_listings      ENABLE ROW LEVEL SECURITY;
ALTER TABLE meal_reservations  ENABLE ROW LEVEL SECURITY;

-- profiles
CREATE POLICY "owner_reads_profile" ON profiles FOR SELECT
  USING (auth.uid() = id OR auth.jwt()->>'role' = 'ADMIN');

CREATE POLICY "owner_updates_profile" ON profiles FOR UPDATE
  USING (auth.uid() = id);

-- telemetry_readings (INSERT via service_role bypass RLS)
CREATE POLICY "farmer_reads_telemetry" ON telemetry_readings FOR SELECT
  USING (farmer_id = auth.uid() OR auth.jwt()->>'role' = 'ADMIN');

-- katara_alerts
CREATE POLICY "farmer_reads_alerts" ON katara_alerts FOR SELECT
  USING (farmer_id = auth.uid() OR auth.jwt()->>'role' = 'ADMIN');

CREATE POLICY "farmer_marks_read" ON katara_alerts FOR UPDATE
  USING (farmer_id = auth.uid());

-- farm_listings (SELECT public)
CREATE POLICY "public_reads_listings" ON farm_listings FOR SELECT
  USING (true);

CREATE POLICY "farmer_creates_listing" ON farm_listings FOR INSERT
  WITH CHECK (auth.jwt()->'user_metadata'->>'role' = 'FARMER');

CREATE POLICY "farmer_owns_listing" ON farm_listings FOR UPDATE
  USING (farmer_id = auth.uid());

-- farm_orders
CREATE POLICY "buyer_or_farmer_reads_order" ON farm_orders FOR SELECT
  USING (
    buyer_id = auth.uid() OR
    listing_id IN (SELECT id FROM farm_listings WHERE farmer_id = auth.uid())
  );

-- botaba9a_leads (INSERT anonyme)
CREATE POLICY "anon_inserts_lead" ON botaba9a_leads FOR INSERT
  WITH CHECK (true);

CREATE POLICY "admin_reads_leads" ON botaba9a_leads FOR SELECT
  USING (auth.jwt()->>'role' = 'ADMIN');

-- meal_listings (SELECT public)
CREATE POLICY "public_reads_meals" ON meal_listings FOR SELECT
  USING (true);

CREATE POLICY "restaurant_owns_meal" ON meal_listings FOR ALL
  USING (restaurant_id = auth.uid());

-- meal_reservations
CREATE POLICY "citizen_creates_reservation" ON meal_reservations FOR INSERT
  WITH CHECK (auth.jwt()->'user_metadata'->>'role' = 'CITIZEN');

CREATE POLICY "citizen_or_restaurant_reads" ON meal_reservations FOR SELECT
  USING (
    citizen_id = auth.uid() OR
    meal_id IN (SELECT id FROM meal_listings WHERE restaurant_id = auth.uid())
  );
```

---

## 9. API Contracts

### 9.1 Convention Générale

```
Base URL Frontend : https://vitachain.ma
Base URL API      : https://api.vitachain.ma

Authentification :
  - JWT Bearer : Authorization: Bearer <token>
  - IoT API Key : X-API-Key: <iot_api_key>

Format réponse :
  - Succès : données directes (pas de wrapper)
  - Erreur : { "error": { "code": "CODE", "message": "..." } }

Format dates : ISO 8601 (ex: "2026-04-24T16:00:00Z")
Format IDs   : UUID v4
Pagination   : ?limit=20&offset=0
```

### 9.2 Auth Endpoints (Supabase Auth managed)

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/auth/v1/signup` | None | Inscription |
| POST | `/auth/v1/token?grant_type=password` | None | Connexion |
| POST | `/auth/v1/recover` | None | Reset password |
| POST | `/auth/v1/logout` | Bearer | Déconnexion |

### 9.3 KATARA Endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/api/telemetry` | X-API-Key | Ingestion données ESP32 |
| GET | `/api/katara/devices` | FARMER | Liste mes capteurs |
| POST | `/api/katara/devices` | FARMER | Enregistrer capteur |
| GET | `/api/katara/dashboard` | FARMER | Données dashboard |
| GET | `/api/katara/history` | FARMER | Historique télémétrie |
| POST | `/api/katara/analyze/{device_id}` | FARMER | Déclencher analyse IA |
| GET | `/api/katara/weather/{device_id}` | FARMER | Données météo |
| GET | `/api/katara/alerts` | FARMER | Liste alertes |
| PATCH | `/api/katara/alerts/{id}/read` | FARMER | Marquer alerte lue |

**POST /api/telemetry — Request Body:**
```json
{
  "device_id": "katara-550e8400-e29b-41d4-a716",
  "temperature": 36.8,
  "humidity": 55.2,
  "ndvi": 0.42,
  "battery_level": 78.5,
  "timestamp": "2026-04-24T14:30:00Z"
}
```

**POST /api/telemetry — Response 200:**
```json
{
  "status": "ok",
  "reading_id": "uuid-...",
  "farmer_notified": false
}
```

### 9.4 FARMARKET Endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/api/farmarket/listings` | None (public) | Liste annonces |
| POST | `/api/farmarket/listings` | FARMER | Créer annonce |
| PATCH | `/api/farmarket/listings/{id}` | FARMER (owner) | Modifier annonce |
| DELETE | `/api/farmarket/listings/{id}` | FARMER (owner) | Archiver annonce |
| POST | `/api/farmarket/orders` | FARMER/CITIZEN | Passer commande |
| GET | `/api/farmarket/orders/my` | Any | Mes commandes |
| GET | `/api/farmarket/orders/incoming` | FARMER | Commandes reçues |
| PATCH | `/api/farmarket/orders/{id}/confirm` | FARMER (owner) | Confirmer commande |
| PATCH | `/api/farmarket/orders/{id}/cancel` | Any (owner) | Annuler commande |

**GET /api/farmarket/listings — Query Params:**
```
?product=tomates
?min_price=5&max_price=15
?lat=33.5&lng=-7.6&radius=100
?limit=20&offset=0
```

**GET /api/farmarket/listings — Response 200:**
```json
{
  "listings": [
    {
      "id": "uuid-...",
      "title": "Tomates cerises bio",
      "product_type": "tomates",
      "quantity_kg": 200.0,
      "price_per_kg": 12.50,
      "status": "active",
      "farmer": { "full_name": "Ahmed B." },
      "created_at": "2026-04-20T10:00:00Z"
    }
  ],
  "total": 42
}
```

### 9.5 SECONDSERVE Endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/api/secondserve/meals` | None (public) | Repas disponibles |
| POST | `/api/secondserve/meals` | RESTAURANT | Créer repas |
| PATCH | `/api/secondserve/meals/{id}` | RESTAURANT (owner) | Modifier repas |
| DELETE | `/api/secondserve/meals/{id}` | RESTAURANT (owner) | Annuler repas |
| GET | `/api/secondserve/reservations/incoming` | RESTAURANT | Réservations reçues |
| POST | `/api/secondserve/validate-pickup/{code}` | RESTAURANT | Valider retrait |
| POST | `/api/secondserve/reservations` | CITIZEN | Réserver |
| GET | `/api/secondserve/reservations/my` | CITIZEN | Mes réservations |
| DELETE | `/api/secondserve/reservations/{id}` | CITIZEN (owner) | Annuler réservation |

**POST /api/secondserve/reservations — Request Body:**
```json
{
  "meal_listing_id": "uuid-...",
  "quantity": 2
}
```

**POST /api/secondserve/reservations — Response 201:**
```json
{
  "reservation_id": "uuid-...",
  "pickup_code": "482951",
  "pickup_start": "2026-04-24T20:00:00Z",
  "pickup_end": "2026-04-24T22:00:00Z",
  "meal_title": "Tajine de Poulet",
  "restaurant_name": "Restaurant Al Mounia"
}
```

### 9.6 Format d'Erreur Standard

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Le champ temperature doit être entre -10 et 60",
    "details": {
      "field": "temperature",
      "value": 200,
      "constraint": "ge=-10, le=60"
    }
  }
}
```

**Codes d'erreur communs :**

| Code | HTTP | Description |
|---|---|---|
| `VALIDATION_ERROR` | 422 | Données invalides (Pydantic) |
| `UNAUTHORIZED` | 401 | Token manquant ou invalide |
| `FORBIDDEN` | 403 | Rôle insuffisant ou pas propriétaire |
| `NOT_FOUND` | 404 | Ressource inexistante |
| `CONFLICT` | 409 | Double booking, code déjà utilisé |
| `GONE` | 410 | Créneau expiré |
| `INTERNAL_ERROR` | 500 | Erreur serveur (pas de détail en production) |

---

## 10. Module Specifications

### 10.1 Module M1 — KATARA

**Objectif :** Collecter, analyser et visualiser les données IoT des capteurs ESP32 installés dans les champs marocains.

**Composants backend :**
```
backend/app/api/routes/
  ├── telemetry.py    # POST /api/telemetry (X-API-Key auth)
  └── katara.py       # Routes dashboard, alertes, analyse

backend/app/services/
  ├── telemetry_service.py  # Logique ingestion + seuils
  ├── ai_service.py         # AsyncAnthropic() → Claude
  ├── weather_service.py    # OpenWeatherMap + cache 15min
  └── satellite_service.py  # Sentinel Hub + cache 24h (V2)
```

**Composants frontend :**
```
frontend/app/(dashboard)/katara/
  ├── dashboard/
  │   ├── page.tsx             # Dashboard principal
  │   ├── components/
  │   │   ├── TelemetryChart.tsx   # recharts courbe temp/humidity
  │   │   ├── AlertPanel.tsx       # Alertes non lues
  │   │   └── WeatherWidget.tsx    # Widget météo
  │   └── hooks/
  │       └── useTelemetry.ts      # Supabase Realtime
  ├── sensors/
  │   └── page.tsx             # Gestion capteurs ESP32
  └── alerts/
      └── page.tsx             # Historique alertes
```

**Flux d'analyse IA :**
1. POST /api/telemetry reçu → insertion Supabase
2. Si lectures >= 10 (7 derniers jours) → déclencher `analyze_farm_telemetry()`
3. Calculer stats : temp_moy, temp_min, temp_max, humidity_moy, ndvi_moy
4. Appel `AsyncAnthropic().messages.create()` avec prompt agronomique
5. Réponse Claude → INSERT dans katara_alerts (type='ai_recommendation')
6. Supabase Realtime → frontend notifié → badge alerte mis à jour

**Prompt system Claude :**
```
Tu es un expert agronome marocain spécialisé dans les grandes cultures
(blé, tomates, agrumes, olivier). Réponds toujours en français.
Tes analyses sont basées sur des données de capteurs IoT terrain.
Format de réponse : bullet points structurés, maximum 800 tokens.
```

---

### 10.2 Module M2 — FARMARKET

**Objectif :** Marketplace B2B permettant aux agriculteurs de vendre directement leurs produits aux restaurants et acheteurs professionnels.

**Règles métier critiques :**
- `farmer_id` est TOUJOURS extrait du JWT — jamais du request body
- DELETE = soft delete (`status = 'expired'`) — la ligne reste en base
- PATCH nécessite vérification `farm_listings.farmer_id == JWT.sub`
- Recherche publique sans authentification obligatoire

**Composants backend :**
```
backend/app/api/routes/farmarket.py
backend/app/services/marketplace_service.py
backend/app/models/marketplace.py
```

**Composants frontend :**
```
frontend/app/(public)/farmarket/        # Pages publiques
  ├── listings/page.tsx                 # Liste publique
  └── listings/[id]/page.tsx           # Détail annonce

frontend/app/(dashboard)/farmarket/    # Pages authentifiées
  ├── listings/
  │   ├── page.tsx                     # Mes annonces
  │   ├── create/page.tsx              # Créer annonce
  │   └── components/
  │       ├── ListingCard.tsx
  │       └── ListingForm.tsx
  └── orders/
      └── page.tsx                     # Commandes
```

---

### 10.3 Module M3 — BOTABA9A

**Objectif :** Vitrine marketing statique pour présenter les solutions IoT de Vitachain aux restaurateurs marocains.

**Caractéristiques techniques :**
- Next.js SSG — `export const dynamic = 'force-static'`
- Aucun backend dédié
- INSERT direct Supabase depuis Next.js API Route
- RLS: INSERT anonyme autorisé sur `botaba9a_leads`
- Lighthouse Performance > 90 sur mobile

**Produits présentés :**
1. Caisse Enregistreuse Intelligente — POS connecté IoT
2. Détecteur de Gaz IoT — Alerte SMS/email en cas de fuite
3. Dashboard Analytics Temps Réel — Métriques restaurant

**Composants frontend :**
```
frontend/app/(public)/botaba9a/
  ├── page.tsx                    # Page d'accueil SSG
  ├── produits/page.tsx           # Détail produits
  ├── contact/page.tsx            # Formulaire contact
  └── components/
      ├── HeroSection.tsx
      ├── ProductCard.tsx
      └── ContactForm.tsx

frontend/app/api/botaba9a/
  └── lead/route.ts               # API Route → INSERT Supabase
```

---

### 10.4 Module M4 — SECONDSERVE

**Objectif :** Permettre aux restaurants de vendre leurs repas invendus en fin de service via un système Click & Collect avec code de retrait unique.

**Règles métier critiques :**
- Réservation atomique via RPC Supabase (pas de double booking)
- `pickup_code` généré CÔTÉ SERVEUR dans la RPC (jamais côté client)
- `restaurant_id` extrait du JWT — jamais du request body
- Annulation possible seulement si `pickup_start > NOW() + 2h`
- Expiration automatique : CRON ou trigger Supabase
- Echec email Brevo ≠ échec de réservation (log WARNING + réservation conservée)

**RPC Supabase — Réservation Atomique :**
```sql
CREATE OR REPLACE FUNCTION create_reservation(
  p_meal_id UUID,
  p_citizen_id UUID,
  p_quantity INT
) RETURNS TABLE(reservation_id UUID, pickup_code TEXT)
LANGUAGE plpgsql AS $$
DECLARE
  v_meal meal_listings%ROWTYPE;
  v_code TEXT;
  v_reservation_id UUID;
BEGIN
  -- Verrouiller la ligne pour éviter le double booking
  SELECT * INTO v_meal FROM meal_listings
  WHERE id = p_meal_id FOR UPDATE;

  -- Validations
  IF v_meal.status != 'available' THEN
    RAISE EXCEPTION 'MEAL_NOT_AVAILABLE';
  END IF;
  IF v_meal.quantity_available < p_quantity THEN
    RAISE EXCEPTION 'INSUFFICIENT_STOCK';
  END IF;
  IF v_meal.pickup_end < NOW() THEN
    RAISE EXCEPTION 'PICKUP_EXPIRED';
  END IF;

  -- Générer code unique
  v_code := lpad(floor(random() * 1000000)::text, 6, '0');

  -- INSERT réservation
  INSERT INTO meal_reservations(meal_id, citizen_id, quantity, pickup_code)
  VALUES (p_meal_id, p_citizen_id, p_quantity, v_code)
  RETURNING id INTO v_reservation_id;

  -- Décrémenter stock atomiquement
  UPDATE meal_listings
  SET quantity_available = quantity_available - p_quantity
  WHERE id = p_meal_id;

  RETURN QUERY SELECT v_reservation_id, v_code;
END;
$$;
```

---

## 11. External Integrations

### 11.1 Claude API (Anthropic)

| Paramètre | Valeur |
|---|---|
| Modèle | `claude-sonnet-4-20250514` |
| max_tokens | 800 |
| Timeout | 30 secondes |
| Client | `anthropic.AsyncAnthropic()` |
| Fallback | Retourner `null`, log `ERROR`, alerte non créée |
| Erreurs gérées | `APITimeoutError`, `RateLimitError`, `APIError` |

**Règle absolue :** Jamais `anthropic.Anthropic()` synchrone dans FastAPI. Utiliser toujours `AsyncAnthropic()` avec `await`.

### 11.2 OpenWeatherMap

| Paramètre | Valeur |
|---|---|
| Endpoint | `api.openweathermap.org/data/2.5/weather` |
| Client | `httpx.AsyncClient()` |
| Cache | 15 minutes (en mémoire) |
| Données | temp, humidity, rain, wind_speed |
| Fallback | Retourner données cachées ou `null` |

### 11.3 Sentinel Hub (V2 — Post-MVD)

| Paramètre | Valeur |
|---|---|
| Usage | Imagerie satellite NDVI |
| Cache | 24 heures |
| Coût | ~200 MAD/mois (plan basique) |
| Fallback | Retourner dernière image disponible |

### 11.4 Brevo (Email)

| Paramètre | Valeur |
|---|---|
| Endpoint | `https://api.brevo.com/v3/smtp/email` |
| Méthode | `httpx.AsyncClient()` POST direct |
| Auth header | `api-key: BREVO_API_KEY` |
| Fallback | Log `WARNING`, action métier conservée |
| Timeout | 10 secondes |

**Règle absolue :** Pas de SDK Brevo Python. Appel direct httpx uniquement.

### 11.5 OpenStreetMap / Leaflet (V2 — Post-MVD)

- Intégration côté frontend uniquement
- Leaflet.js pour affichage carte
- Pas d'appel backend requis

---

## 12. Security Requirements

### 12.1 Infrastructure

```nginx
# NGINX — headers sécurité obligatoires
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
add_header X-Frame-Options "DENY" always;
add_header X-Content-Type-Options "nosniff" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;

# Rate limiting
limit_req_zone $binary_remote_addr zone=iot:10m rate=30r/m;
limit_req_zone $binary_remote_addr zone=api:10m rate=60r/m;
```

### 12.2 Secrets Management

```
# Variables d'environnement obligatoires — jamais dans le code
SUPABASE_URL                    # URL Supabase Cloud
SUPABASE_SERVICE_KEY            # Clé backend (bypass RLS) — JAMAIS dans le frontend
SUPABASE_ANON_KEY               # Clé frontend uniquement
SUPABASE_JWT_SECRET             # Pour valider les JWT backend
ANTHROPIC_API_KEY               # Claude AI
OPENWEATHER_API_KEY             # Météo
SENTINEL_HUB_KEY                # Satellite (V2)
BREVO_API_KEY                   # Emails
IOT_API_KEY                     # Authentification ESP32

# Next.js public (exposées côté client — inoffensives)
NEXT_PUBLIC_SUPABASE_URL
NEXT_PUBLIC_SUPABASE_ANON_KEY
```

### 12.3 Règles Sécurité Code

- `SUPABASE_SERVICE_KEY` : backend uniquement, jamais dans le frontend
- `SUPABASE_ANON_KEY` : frontend uniquement, jamais dans le backend (permissions insuffisantes)
- JWT stocké en cookie `httpOnly` uniquement — jamais `localStorage`
- Jamais de `try/except: pass` — toujours `logging.error()`
- Jamais de stacktrace dans les réponses HTTP
- IOT_API_KEY : rotation recommandée tous les 90 jours
- `.env` dans `.gitignore` — validation à chaque commit via pre-commit hook

### 12.4 GDPR

- Suppression compte : supprimer ou anonymiser toutes les données utilisateur
- Export données : endpoint disponible (post-MVD)
- Logs : rétention 90 jours maximum
- Telemetry : propriété du farmer, inaccessible aux autres via RLS

---

## 13. MVP Scope & Exclusions

### 13.1 Dans le Scope MVD (8 semaines)

| Epic | Stories | Priorité |
|---|---|---|
| Epic 0 — Infrastructure | 0-1 à 0-5 | P0 — Obligatoire en premier |
| Epic 1 — Auth | 1-1, 1-2, 1-4, 1-6 | P0 |
| Epic 2 — KATARA | 2-1, 2-2, 2-3, 2-5, 2-6, 2-8, 2-9, 2-11 | P0/P1 |
| Epic 3 — FARMARKET | 3-1, 3-2, 3-3, 3-5 | P0/P1 |
| Epic 4 — SECONDSERVE | 4-1, 4-6, 4-8, 4-11, 4-43 | P0/P1 |
| Epic 5 — BOTABA9A | 5-1, 5-2, 5-3 | P0/P1 |
| Epic 8 — Notifications | 8-1, 8-3, 8-4 | P1 |

### 13.2 Hors Scope MVD (V2 — Post-lancement)

| Feature | Justification |
|---|---|
| Paiements (CIB, PayPal) | Complexité légale et technique |
| Application mobile React Native | Effort trop important pour MVD |
| Imagerie satellite NDVI (Sentinel Hub) | Coût + complexité |
| Support multilingue (Arabe, Français) | Post-MVD — Anglais d'abord |
| Dashboard Admin avancé (Epic 6) | Pas nécessaire pour lancer |
| Module Support Client (Epic 7) | Email de contact suffisant au lancement |
| CI/CD automatisé | Déploiement manuel suffisant pour MVD |
| Monitoring avancé (Sentry, Prometheus) | Docker logs suffisants pour MVD |
| PWA / Offline mode | Post-MVD |
| Système de notation/avis | Post-MVD |
| Géolocalisation avancée (Leaflet) | Post-MVD |
| 1-3 Magic Link Auth | Supabase le supporte nativement, priorité basse |
| 1-7 Admin User Management | Post-MVD |
| 1-8 Suspicious Login Detection | Post-MVD |
| 2-7 Satellite NDVI | Post-MVD (coût) |
| Commandes FARMARKET complètes (3-6 à 3-11) | V1.1 |
| SECONDSERVE avancé (4-2 à 4-13) | Réservation basique suffit pour MVD |

---

## 14. Implementation Timeline

### Semaine 1 — Infrastructure & Base de Données

**Objectif :** Avoir l'infrastructure complète opérationnelle.

| Jour | Tâche | Story |
|---|---|---|
| J1-J2 | VPS DigitalOcean + Docker + UFW | 0-1 |
| J2-J3 | docker-compose.yml + réseau interne | 0-2 |
| J3-J4 | NGINX config + SSL Certbot | 0-3 |
| J4-J5 | Supabase SQL + RLS + Triggers | 0-4 |
| J5 | Variables .env + .gitignore | 0-5 |

**Critère de succès S1 :** `docker compose up` démarre 5 containers. HTTPS fonctionne sur vitachain.ma et api.vitachain.ma.

### Semaine 2 — Auth + KATARA Base

**Objectif :** Inscription/connexion fonctionnelle. Premier capteur ESP32 enregistré.

| Jour | Tâche | Story |
|---|---|---|
| J6-J7 | Inscription + vérification email | 1-1 |
| J7-J8 | Connexion + JWT cookie + middleware | 1-2 |
| J8 | Reset mot de passe | 1-4 |
| J8-J9 | RBAC middleware frontend + backend | 1-6 |
| J9-J10 | Enregistrement device ESP32 | 2-1 |
| J10 | Ingestion télémétrie POST /api/telemetry | 2-2 |

**Critère de succès S2 :** Un utilisateur peut s'inscrire. Un simulated ESP32 (curl) envoie des données qui apparaissent en base.

### Semaines 3-4 — KATARA Complet + FARMARKET

**Objectif :** Dashboard KATARA fonctionnel. Annonces FARMARKET créables.

| Tâche | Story |
|---|---|
| Dashboard temps réel + recharts | 2-3 |
| Analyse IA Claude + alertes | 2-5 |
| Intégration météo OpenWeatherMap | 2-6 |
| Alertes seuil automatiques | 2-11 |
| Gestion alertes lu/non lu | 2-8, 2-9 |
| CRUD annonces FARMARKET | 3-1, 3-2 |
| Navigation publique + filtres | 3-3, 3-5 |

### Semaines 5-6 — SECONDSERVE + BOTABA9A

**Objectif :** Un restaurant peut publier un repas. Un citoyen peut réserver et recevoir son email.

| Tâche | Story |
|---|---|
| Création repas restaurant | 4-1 |
| Navigation repas publique | 4-6 |
| Réservation atomique + code retrait | 4-8, 4-11 |
| Email confirmation Brevo | 8-3, 8-4 |
| Validation code retrait | 4-5 (partiel) |
| Vitrine Botaba9a SSG | 5-1, 5-2, 5-3 |

### Semaines 7-8 — Intégration, Tests, Déploiement

**Objectif :** Tous les modules fonctionnent ensemble en production.

| Tâche | Description |
|---|---|
| Emails KATARA | Alertes critiques → email Brevo |
| Tests end-to-end | Parcours complet pour chaque rôle |
| Optimisation performance | Lighthouse > 90, vérifier <50ms telemetry |
| Déploiement VPS | `docker compose up -d` en production |
| DNS + HTTPS | vitachain.ma → VPS, SSL Let's Encrypt |
| Monitoring | Docker logs, Supabase dashboard |
| Documentation | README déploiement + guide utilisateur |

---

## 15. Success Metrics

### 15.1 Métriques Techniques (MVD)

| Métrique | Cible | Mesure |
|---|---|---|
| Ingestion télémétrie | < 50ms | Timer FastAPI |
| Réponse API (P95) | < 200ms | NGINX access logs |
| Uptime | > 99.9% | Monitoring externe |
| Lighthouse Performance | > 90 (mobile) | Google Lighthouse |
| Erreurs 5xx | < 0.1% des requêtes | NGINX error logs |
| Temps analyse Claude | < 30s | Application logs |

### 15.2 Métriques Produit (3 mois post-lancement)

| Métrique | Cible |
|---|---|
| Agriculteurs inscrits | 50 |
| Capteurs ESP32 actifs | 100 |
| Annonces FARMARKET actives | 200 |
| Réservations SECONDSERVE | 500/mois |
| Taux conversion lead Botaba9a | > 5% |
| NPS (Net Promoter Score) | > 40 |

---

## 16. Risks & Mitigations

| Risque | Probabilité | Impact | Mitigation |
|---|---|---|---|
| Claude API trop lent / timeout | Moyen | Moyen | Timeout 30s, fallback null, cache résultats |
| Supabase free tier saturé (500 MB) | Moyen | Haut | Monitoring quotidien, purge données anciennes, upgrade ~25$/mois |
| ESP32 envoie des données malformées | Élevé | Faible | Validation Pydantic stricte, 422 retourné |
| Double booking sur SECONDSERVE | Faible | Haut | RPC Supabase transactionnelle avec SELECT FOR UPDATE |
| Brevo down → emails perdus | Faible | Moyen | Log WARNING, réservation conservée, retry manuel si besoin |
| VPS DigitalOcean down | Très faible | Critique | Supabase backups 30j, snapshot VPS hebdomadaire |
| Clé API leakée dans Git | Faible | Critique | .gitignore + pre-commit hook + audit mensuel |
| Connexion 3G trop lente pour farmers | Élevé | Moyen | Optimisation 3G-aware, images compressées, SSG |
| BMAD génère du code générique | Élevé | Moyen | Prompt Maître v2.0 en début de chaque session |

---

## Appendix A — Variables d'Environnement Complètes

```bash
# ============================================================
# VITACHAIN — .env.example
# ============================================================

# === SUPABASE ===
SUPABASE_URL=https://xxxxxxxxxxxx.supabase.co
SUPABASE_SERVICE_KEY=eyJhbG...  # Backend SEULEMENT — accès complet, bypass RLS
SUPABASE_ANON_KEY=eyJhbG...     # Frontend SEULEMENT — respecte RLS
SUPABASE_JWT_SECRET=your-jwt-secret  # Dashboard Supabase → Settings → API → JWT Secret

# Next.js — exposées côté client (inoffensives)
NEXT_PUBLIC_SUPABASE_URL=https://xxxxxxxxxxxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbG...

# === INTELLIGENCE ARTIFICIELLE ===
ANTHROPIC_API_KEY=sk-ant-api03-...    # console.anthropic.com → API Keys

# === MÉTÉO ===
OPENWEATHER_API_KEY=abc123...         # openweathermap.org → Account → API Keys

# === IMAGERIE SATELLITE (V2) ===
SENTINEL_HUB_KEY=your-key             # sentinel-hub.com (plan ~200 MAD/mois)

# === EMAIL ===
BREVO_API_KEY=xsmtpx...               # brevo.com → SMTP & API → API Keys

# === IOT CAPTEURS ===
IOT_API_KEY=katara-secret-key-2024    # Valeur personnalisée — à flasher dans l'ESP32

# === DOMAINES ===
DOMAIN=vitachain.ma
API_DOMAIN=api.vitachain.ma
```

---

## Appendix B — Ordre d'Implémentation Recommandé

```
OBLIGATOIRE EN PREMIER (bloquant pour tout le reste)
├── Epic 0 — Infrastructure
│   ├── 0-1 VPS + Docker
│   ├── 0-2 Docker Compose
│   ├── 0-3 NGINX + SSL
│   ├── 0-4 Supabase SQL + RLS
│   └── 0-5 Variables .env
│
AUTHENTIFICATION (bloquant pour les modules)
├── Epic 1 — Auth
│   ├── 1-1 Inscription
│   ├── 1-2 Connexion
│   ├── 1-4 Reset password
│   └── 1-6 RBAC
│
MODULES MÉTIER (peuvent être parallélisés)
├── Epic 2 — KATARA
│   ├── 2-1 Device registration
│   ├── 2-2 Telemetry ingestion  ← Tester avec curl simulant ESP32
│   ├── 2-3 Dashboard realtime
│   ├── 2-11 Alertes seuil
│   ├── 2-5 Analyse IA Claude
│   ├── 2-6 Météo
│   └── 2-8/2-9 Alertes lu/non lu
│
├── Epic 3 — FARMARKET
│   ├── 3-1 Créer annonce
│   ├── 3-2 Modifier/supprimer
│   ├── 3-3 Navigation publique
│   └── 3-5 Filtres
│
├── Epic 4 — SECONDSERVE
│   ├── 4-1 Créer repas
│   ├── 4-6 Navigation publique
│   ├── 4-8 Réservation atomique
│   └── 4-11 Code retrait
│
├── Epic 5 — BOTABA9A
│   ├── 5-1 Pages statiques
│   └── 5-2/5-3 Formulaire lead
│
NOTIFICATIONS (dépendent des modules)
└── Epic 8 — Notifications
    ├── 8-1 Emails alertes KATARA
    ├── 8-3 Emails confirmation réservation
    └── 8-4 Email code retrait
```

---

*Vitachain v1.0 PRD — Document de Référence Produit*
*Dernière mise à jour : 2026-05-01*
*Statut : Approved for Development*