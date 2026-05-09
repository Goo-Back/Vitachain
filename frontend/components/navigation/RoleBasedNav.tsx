"use client";

// Role-based navigation component
interface RoleBasedNavProps {
  userRole?: string;
}

export function RoleBasedNav({ userRole }: RoleBasedNavProps) {
  const getNavItems = () => {
    if (!userRole) {
      return [
        { name: 'Connexion', href: '/auth/login', icon: '🔐' },
        { name: 'Inscription', href: '/auth/register', icon: '📝' }
      ];
    }

    const roleNavItems: Record<string, Array<{name: string, href: string, icon: string}>> = {
      'FARMER': [
        { name: 'Tableau de Bord', href: '/dashboard/katara', icon: '🌾' },
        { name: 'Mes Appareils', href: '/dashboard/katara/devices', icon: '📱' },
        { name: 'Télémétrie', href: '/dashboard/katara/telemetry', icon: '📊' },
        { name: 'Alertes', href: '/dashboard/katara/alerts', icon: '🚨' },
        { name: 'Mes Annonces', href: '/dashboard/farmarket', icon: '🛒' },
        { name: 'Profil', href: '/profile', icon: '👤' }
      ],
      'RESTAURANT': [
        { name: 'Tableau de Bord', href: '/dashboard/secondserve', icon: '🍽' },
        { name: 'Mes Repas', href: '/dashboard/secondserve/meals', icon: '🍲' },
        { name: 'Réservations', href: '/dashboard/secondserve/reservations', icon: '📋' },
        { name: 'Marketplace', href: '/dashboard/farmarket', icon: '🛒' },
        { name: 'Profil', href: '/profile', icon: '👤' }
      ],
      'CITIZEN': [
        { name: 'Marketplace', href: '/dashboard/farmarket', icon: '🛒' },
        { name: 'Mes Réservations', href: '/dashboard/secondserve/reservations', icon: '📋' },
        { name: 'Profil', href: '/profile', icon: '👤' }
      ],
      'ADMIN': [
        { name: 'Administration', href: '/dashboard/admin', icon: '⚙️' },
        { name: 'Utilisateurs', href: '/dashboard/admin/users', icon: '👥' },
        { name: 'Système', href: '/dashboard/admin/system', icon: '🖥️' },
        { name: 'Audit Logs', href: '/dashboard/admin/audit', icon: '📝' },
        { name: 'Support', href: '/dashboard/support', icon: '💬' }
      ],
      'SUPPORT': [
        { name: 'Support', href: '/dashboard/support', icon: '💬' },
        { name: 'Utilisateurs', href: '/dashboard/support/users', icon: '👥' },
        { name: 'Tickets', href: '/dashboard/support/tickets', icon: '🎫' },
        { name: 'Audit Logs', href: '/dashboard/support/audit', icon: '📝' }
      ]
    };

    return roleNavItems[userRole] || [];
  };

  const navItems = getNavItems();

  return (
    <nav className="bg-white shadow-md rounded-lg overflow-hidden">
      <div className="px-4 py-3">
        <h2 className="text-lg font-semibold text-gray-800 mb-4">
          Navigation {userRole && `- ${userRole}`}
        </h2>
        
        <ul className="space-y-2">
          {navItems.map((item, index) => (
            <li key={index}>
              <a
                href={item.href}
                className="flex items-center p-2 text-gray-700 rounded-md hover:bg-gray-100 hover:text-gray-900 transition-colors duration-200"
              >
                <span className="mr-3 text-xl">{item.icon}</span>
                <span className="font-medium">{item.name}</span>
              </a>
            </li>
          ))}
        </ul>
      </div>
    </nav>
  );
}

export default RoleBasedNav;
