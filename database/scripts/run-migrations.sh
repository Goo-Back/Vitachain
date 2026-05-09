#!/bin/bash

# VitaChain Manual Migration Runner
# Ce script exécute les migrations SQL directement via la base de données

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Logging
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }

# Database connection info
DB_URL="postgresql://postgres:%26tcb-HU%2A2f5a8%25x@db.bgdtqvpchfnrscupyyaa.supabase.co:5432/postgres"

# Check if psql is available
if ! command -v psql &> /dev/null; then
    log_error "psql is not installed. Please install PostgreSQL client tools."
    log_info "On Ubuntu/WSL: sudo apt-get install postgresql-client"
    exit 1
fi

# Migration files in order
MIGRATIONS=(
    "migrations/01-schema.sql"
    "migrations/02-rls-policies.sql"
    "migrations/03-functions.sql"
    "migrations/04-triggers.sql"
    "migrations/05-indexes.sql"
    "migrations/06-seed-data.sql"
)

# Config files
CONFIG_FILES=(
    "config/extensions.sql"
    "config/database-config.sql"
)

# Function to run a single migration
run_migration() {
    local file="$1"
    local description="$2"
    
    log_info "Exécution: $description"
    log_info "Fichier: $file"
    
    if [[ ! -f "$file" ]]; then
        log_error "Fichier non trouvé: $file"
        return 1
    fi
    
    # Execute the migration
    if PGPASSWORD="&tcb-HU*2f5a8%x" psql "$DB_URL" -f "$file"; then
        log_success "Migration réussie: $description"
        return 0
    else
        log_error "Migration échouée: $description"
        return 1
    fi
}

# Main execution
main() {
    log_info "Démarrage de l'exécution manuelle des migrations VitaChain..."
    echo ""
    
    # Check database connection
    log_info "Test de connexion à la base de données..."
    if PGPASSWORD="&tcb-HU*2f5a8%x" psql "$DB_URL" -c "SELECT 1;" > /dev/null 2>&1; then
        log_success "Connexion à la base de données réussie"
    else
        log_error "Impossible de se connecter à la base de données"
        log_info "Vérifiez l'URL et le mot de passe dans les variables d'environnement"
        exit 1
    fi
    echo ""
    
    # Run migrations
    log_info "Exécution des migrations principales..."
    echo ""
    
    for i in "${!MIGRATIONS[@]}"; do
        migration="${MIGRATIONS[$i]}"
        description="Migration $((i+1))/6: $(basename "$migration" .sql | sed 's/^[0-9]*-//')"
        
        if run_migration "$migration" "$description"; then
            echo ""
        else
            log_error "Arrêt de l'exécution due à une erreur de migration"
            exit 1
        fi
    done
    
    # Run config files
    log_info "Exécution des fichiers de configuration..."
    echo ""
    
    for config_file in "${CONFIG_FILES[@]}"; do
        if [[ -f "$config_file" ]]; then
            description="Configuration: $(basename "$config_file" .sql)"
            
            if run_migration "$config_file" "$description"; then
                echo ""
            else
                log_warning "Configuration échouée (peut être optionnelle): $description"
                echo ""
            fi
        else
            log_warning "Fichier de configuration non trouvé: $config_file"
        fi
    done
    
    # Final verification
    log_info "Vérification finale..."
    echo ""
    
    # Check if key tables exist
    key_tables=("users" "user_profiles" "roles" "devices" "telemetry")
    for table in "${key_tables[@]}"; do
        if PGPASSWORD="&tcb-HU*2f5a8%x" psql "$DB_URL" -c "SELECT COUNT(*) FROM $table;" > /dev/null 2>&1; then
            log_success "Table $table vérifiée"
        else
            log_error "Table $table non trouvée"
        fi
    done
    
    echo ""
    log_success "Toutes les migrations ont été exécutées avec succès !"
    echo ""
    log_info "Prochaines étapes :"
    echo "1. Exécutez le script de verification: ./scripts/verify-final.sh"
    echo "2. Exécutez le script de test: ./scripts/test-working.sh"
    echo "3. Commencez l'intégration avec l'application VitaChain"
}

# Run main function
main "$@"
