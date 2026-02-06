import { Plane } from 'lucide-react';

const Header = () => {
    return (
        <header className="h-16 bg-white border-b border-border flex items-center px-6 shadow-sm">
            <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-primary/10 rounded-full flex items-center justify-center text-primary">
                    <Plane size={24} className="transform -rotate-45" />
                </div>
                <h1 className="text-2xl font-brand text-secondary tracking-wide">TestFly AI</h1>
            </div>
        </header>
    );
};

export default Header;
