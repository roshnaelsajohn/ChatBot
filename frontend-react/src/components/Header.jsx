import { Plane } from 'lucide-react';

const Header = () => {
    return (
        <header className="h-14 md:h-16 bg-white border-b border-border flex items-center px-4 md:px-6 shadow-sm">
            <div className="flex items-center gap-2 md:gap-3">
                <div className="w-8 h-8 md:w-10 md:h-10 bg-primary/10 rounded-full flex items-center justify-center text-primary">
                    <Plane size={18} className="transform -rotate-45 md:hidden" />
                    <Plane size={24} className="transform -rotate-45 hidden md:block" />
                </div>
                <h1 className="text-xl md:text-2xl font-brand text-secondary tracking-wide">TestFly AI</h1>
            </div>
        </header>
    );
};

export default Header;
