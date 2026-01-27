import { MessageCircle, FileText } from 'lucide-react';
import { NavLink } from 'react-router-dom';

const Navigation = () => {
    const navItems = [
        { path: '/dashboard', label: 'Ask AI', icon: MessageCircle },
        { path: '/documents', label: 'Documents', icon: FileText },
    ];

    return (
        <nav className="w-64 h-full bg-secondary border-r border-slate-700 flex flex-col py-6">
            <div className="px-4 mb-6">
                <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Menu</span>
            </div>
            <div className="flex flex-col gap-1 px-3">
                {navItems.map((item) => (
                    <NavLink
                        key={item.path}
                        to={item.path}
                        className={({ isActive }) => `
                            flex items-center gap-3 px-3 py-3 rounded-lg text-sm font-medium transition-all
                            ${isActive
                                ? 'bg-primary text-white shadow-md'
                                : 'text-slate-400 hover:bg-slate-800 hover:text-white'}
                        `}
                    >
                        <item.icon size={20} />
                        {item.label}
                    </NavLink>
                ))}
            </div>
        </nav>
    );
};

export default Navigation;
