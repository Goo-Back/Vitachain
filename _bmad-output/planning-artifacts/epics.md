---
stepsCompleted: ["validate-prerequisites"]
inputDocuments: ["prd.md", "architecture-decisions.md"]
---

# VitaChain - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for VitaChain, decomposing the requirements from the PRD, UX Design if it exists, and Architecture requirements into implementable stories.

## Requirements Inventory

### Functional Requirements

FR1: Inscription utilisateur avec email + vérification
FR2: Connexion email/mot de passe avec JWT httpOnly
FR3: Magic link authentication
FR4: Réinitialisation mot de passe par email
FR5: Gestion profil (nom, téléphone, rôle)
FR6: Contrôle accès basé sur les rôles (RBAC)
FR7: Tableau de bord gestion utilisateurs (admin)
FR8: Détection connexions suspectes
FR9: Blocage temporaire de compte
FR10: Déconnexion + invalidation session
FR11: Enregistrement device IoT ESP32
FR12: Ingestion données télémétrie ESP32 (<50ms)
FR13: Visualisation temps réel dashboard
FR14: Historique télémétrie avec analyse de tendances
FR15: Recommandations IA agronomiques (Claude API)
FR16: Intégration données météo (OpenWeatherMap)
FR17: Imagerie satellite NDVI (Sentinel Hub)
FR18: Système d'alertes conditions critiques
FR19: Gestion alertes lu/non-lu
FR20: Génération automatique recommandations IA
FR21: Déclenchement alertes sur dépassement seuil
FR22: Création annonce produit agricole
FR23: Modification et suppression annonce
FR24: Navigation publique des annonces
FR25: Recherche géolocalisée (OpenStreetMap)
FR26: Filtres : produit, localisation, prix
FR27: Passation commande B2B
FR28: Historique et statut commandes (acheteur)
FR29: Annulation commande en attente
FR30: Vue commandes reçues (farmer)
FR31: Confirmation/annulation commande (farmer)
FR32: Suivi statut commande
FR33: Création annonce repas (restaurant)
FR34: Définition créneau de retrait
FR35: Modification et suppression annonce repas
FR36: Vue réservations pour restaurants
FR37: Validation code de retrait physique
FR38: Navigation repas disponibles (citoyen)
FR39: Recherche par localisation/prix/cuisine
FR40: Réservation repas (atomique, sans double booking)
FR41: Historique réservations (citoyen)
FR42: Annulation réservation (>2h avant pickup)
FR43: Génération code retrait unique (6 chiffres)
FR44: Expiration automatique annonce repas
FR45: Expiration automatique créneaux réservation
FR46: Pages marketing statiques (SSG)
FR47: Formulaire de contact lead
FR48: Capture et stockage lead (botaba9a_leads)
FR49: Affichage fiches produits IoT
FR50: Dashboard métriques santé système
FR51: Monitoring statut capteurs IoT
FR52: Approbation inscription utilisateurs
FR53: Statistiques d'utilisation plateforme
FR54: Détection et blocage comportements abusifs
FR55: Consultation journaux d'audit
FR56: Métriques et alertes performance
FR57: Détection anomalies trafic API / capteurs
FR58: Gestion tickets support
FR59: Vue informations compte utilisateur
FR60: Libération blocage sécurité
FR61: Réinitialisation code de retrait
FR62: Accès base de connaissances
FR63: Soumission demande support (utilisateur)
FR64: Suivi statut ticket
FR65: Emails notifications alertes KATARA
FR66: Emails notifications commandes FARMARKET
FR67: Emails confirmations réservations SECONDSERVE
FR68: Emails confirmation code de retrait
FR69: Emails notifications leads BOTABA9A
FR70: Notifications in-app temps réel

### NonFunctional Requirements

NFR1: Ingestion télémétrie IoT < 50ms
NFR2: Réponse API REST < 200ms (P95)
NFR3: Chargement pages publiques < 2.5s (connexion 4G)
NFR4: Chargement dashboards < 3.0s (connexion 4G)
NFR5: Mises à jour temps réel < 2s
NFR6: Appels Claude API < 30s
NFR7: Support de 10 à 1 000 utilisateurs actifs simultanés
NFR8: Croissance 10x avec < 10% de dégradation de performance
NFR9: Uptime cible 99.9% (< 8.7h de downtime/an)
NFR10: Zero data loss pour les données de télémétrie
NFR11: RTO (Recovery Time Objective) 4 heures
NFR12: RPO (Recovery Point Objective) 15 minutes
NFR13: Backups automatiques quotidiens Supabase (rétention 30 jours)
NFR14: Chiffrement en transit HTTPS/TLS 1.3 (Let's Encrypt)
NFR15: Chiffrement au repos PostgreSQL Supabase (géré)
NFR16: Authentification JWT Supabase, expiry 24h, refresh 30 jours
NFR17: Autorisation RLS au niveau base de données
NFR18: API Key IoT rotation tous les 90 jours
NFR19: Conformité GDPR suppression données sur demande
NFR20: Jamais de clé secrète dans le code source ou Git
NFR21: WCAG 2.1 niveau AA
NFR22: Support RTL pour l'arabe (post-MVD)
NFR23: Mobile-first design
NFR24: Optimisation 3G pour les zones rurales
NFR25: Navigateurs modernes uniquement (Chrome 90+, Firefox 90+, Safari 14+)
NFR26: Responsive 320px → 1920px
NFR27: PWA-ready (post-MVD)

### Additional Requirements

- Infrastructure deployment on DigitalOcean VPS with Docker Compose
- NGINX reverse proxy with SSL termination and security headers
- Supabase PostgreSQL as primary database with RLS policies
- Async FastAPI backend with separate services per module
- Next.js 14 frontend with TypeScript and Tailwind CSS
- Direct Supabase client usage (no SQLAlchemy ORM)
- JWT authentication with httpOnly cookies
- Row Level Security for all data access
- Rate limiting per IP and endpoint type
- Structured logging with health check endpoints
- Redis caching for frequently accessed data
- Database indexing strategy for time-series and geographic queries
- AI integration via Claude API with async patterns
- Email integration via direct HTTP to Brevo (no SDK)
- Real-time updates via Supabase Realtime WebSocket
- Container-based deployment with internal Docker network
- Environment variable secrets management
- Performance monitoring and alerting
- Database backup and recovery procedures

### UX Design Requirements

No UX Design document found - this section will be populated if UX specifications are available.

### FR Coverage Map

FR1: Epic 2 - User registration with email verification
FR2: Epic 2 - Email/password login with JWT httpOnly
FR3: Epic 2 - Magic link authentication
FR4: Epic 2 - Password reset via email
FR5: Epic 2 - Profile management (name, phone, role)
FR6: Epic 2 - Role-based access control (RBAC)
FR7: Epic 2 - Admin user management dashboard
FR8: Epic 2 - Suspicious login detection
FR9: Epic 2 - Temporary account blocking
FR10: Epic 2 - Logout and session invalidation
FR11: Epic 3 - ESP32 IoT device registration
FR12: Epic 3 - ESP32 telemetry data ingestion (<50ms)
FR13: Epic 3 - Real-time dashboard visualization
FR14: Epic 3 - Telemetry history with trend analysis
FR15: Epic 3 - AI agronomic recommendations (Claude API)
FR16: Epic 3 - Weather data integration (OpenWeatherMap)
FR17: Epic 3 - Satellite NDVI imagery (Sentinel Hub)
FR18: Epic 3 - Critical condition alert system
FR19: Epic 3 - Alert read/unread management
FR20: Epic 3 - Automatic AI recommendation generation
FR21: Epic 3 - Threshold-based alert triggering
FR22: Epic 4 - Agricultural product listing creation
FR23: Epic 4 - Listing modification and deletion
FR24: Epic 4 - Public listing navigation
FR25: Epic 4 - Geolocation-based search (OpenStreetMap)
FR26: Epic 4 - Product, location, price filters
FR27: Epic 4 - B2B order placement
FR28: Epic 4 - Buyer order history and status
FR29: Epic 4 - Pending order cancellation
FR30: Epic 4 - Farmer received orders view
FR31: Epic 4 - Farmer order confirmation/cancellation
FR32: Epic 4 - Order status tracking
FR33: Epic 5 - Restaurant meal listing creation
FR34: Epic 5 - Pickup time slot definition
FR35: Epic 5 - Meal listing modification/deletion
FR36: Epic 5 - Restaurant reservations view
FR37: Epic 5 - Physical pickup code validation
FR38: Epic 5 - Public available meals navigation
FR39: Epic 5 - Location/price/cuisine search
FR40: Epic 5 - Atomic meal reservation (no double booking)
FR41: Epic 5 - Citizen reservation history
FR42: Epic 5 - Reservation cancellation (>2h before pickup)
FR43: Epic 5 - Unique pickup code generation (6 digits)
FR44: Epic 5 - Automatic meal listing expiration
FR45: Epic 5 - Automatic reservation slot expiration
FR46: Epic 6 - Static marketing pages (SSG)
FR47: Epic 6 - Contact lead form
FR48: Epic 6 - Lead capture and storage (botaba9a_leads)
FR49: Epic 6 - IoT product showcase display
FR50: Epic 7 - System health metrics dashboard
FR51: Epic 7 - IoT sensor status monitoring
FR52: Epic 7 - User registration approval
FR53: Epic 7 - Platform usage statistics
FR54: Epic 7 - Abuse detection and blocking
FR55: Epic 7 - Audit log consultation
FR56: Epic 7 - Performance metrics and alerts
FR57: Epic 7 - API/sensor traffic anomaly detection
FR58: Epic 8 - Support ticket management
FR59: Epic 8 - User account information view
FR60: Epic 8 - Security block release
FR61: Epic 8 - Pickup code reset
FR62: Epic 8 - Knowledge base access
FR63: Epic 8 - User support request submission
FR64: Epic 8 - Ticket status tracking
FR65: Epic 9 - KATARA alert email notifications
FR66: Epic 9 - FARMARKET order email notifications
FR67: Epic 9 - SECONDSERVE reservation confirmation emails
FR68: Epic 9 - Pickup code confirmation emails
FR69: Epic 9 - BOTABA9A lead notification emails
FR70: Epic 9 - Real-time in-app notifications

## Epic List

### Epic 1: Platform Foundation & Infrastructure
Establish the complete technical foundation including VPS deployment, Docker containers, NGINX proxy, Supabase database, and all core infrastructure services. This enables all subsequent user-facing functionality.
**FRs covered:** None (infrastructure epic)
**NFRs covered:** NFR1-NFR27 (all performance, security, scalability requirements)

### Epic 2: User Authentication & Profiles
Complete user management system allowing farmers, restaurants, citizens, and administrators to register, authenticate, manage profiles, and access role-based functionality across the platform.
**FRs covered:** FR1-FR10

### Epic 3: Smart Farming with IoT (KATARA)
Farmers can register ESP32 devices, receive real-time telemetry data, view dashboards, get AI agronomic recommendations, and receive critical alerts about their crops' conditions.
**FRs covered:** FR11-FR21

### Epic 4: B2B Agricultural Marketplace (FARMARKET)
Farmers can create and manage product listings, while buyers can browse, search, and place orders for agricultural products in a transparent B2B marketplace.
**FRs covered:** FR22-FR32

### Epic 5: Surplus Food Marketplace (SECONDSERVE)
Restaurants can post unsold meals with pickup time slots, while citizens can discover, reserve, and collect meals at reduced prices using unique pickup codes.
**FRs covered:** FR33-FR45

### Epic 6: IoT Marketing Showcase (BOTABA9A)
Static marketing website showcasing IoT solutions for restaurants, with lead capture forms to generate business opportunities for VitaChain's restaurant technology offerings.
**FRs covered:** FR46-FR49

### Epic 7: Platform Administration & Monitoring
Administrators can monitor system health, manage user accounts, view platform statistics, detect abuse, and access audit logs to maintain platform integrity and performance.
**FRs covered:** FR50-FR57

### Epic 8: Customer Support System
Support agents can manage tickets, view user accounts, resolve issues, and access knowledge base to help users with account problems, reservation issues, and platform questions.
**FRs covered:** FR58-FR64

### Epic 9: Communications & Notifications
Automated email and in-app notifications for critical alerts, order confirmations, pickup codes, and lead follow-ups to keep users informed across all platform interactions.
**FRs covered:** FR65-FR70
