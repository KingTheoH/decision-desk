import { NavLink } from "react-router-dom";
import { clsx } from "clsx";
import {
  LayoutDashboard, Inbox, List, Building2, Briefcase,
  TrendingUp, Film, GitCompare, ClipboardCheck,
  Sliders, BookOpen, Settings, Zap,
} from "lucide-react";

const sections = [
  { label: "Dashboard",      to: "/",           icon: LayoutDashboard },
  { label: "Inbox",          to: "/decisions?status=Inbox",  icon: Inbox },
  { label: "All Decisions",  to: "/decisions",  icon: List },
  { divider: true },
  { label: "Properties",     to: "/properties", icon: Building2 },
  { label: "Business Ideas", to: "/business",   icon: Briefcase },
  { label: "Investments",    to: "/investments",icon: TrendingUp },
  { label: "Content Ideas",  to: "/content",    icon: Film },
  { divider: true },
  { label: "Compare",        to: "/compare",    icon: GitCompare },
  { label: "Review Queue",   to: "/review",     icon: ClipboardCheck },
  { label: "Rubrics",        to: "/rubrics",    icon: Sliders },
  { label: "Journal",        to: "/journal",    icon: BookOpen },
  { divider: true },
  { label: "Settings",       to: "/settings",   icon: Settings },
];

export default function Sidebar() {
  return (
    <aside className="w-52 shrink-0 flex flex-col h-screen bg-surface-1 border-r border-border">
      {/* Brand */}
      <div className="px-4 py-5 border-b border-border">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-md bg-violet-600 flex items-center justify-center">
            <Zap size={14} className="text-white" />
          </div>
          <div>
            <div className="text-sm font-semibold text-zinc-100 leading-tight">Decision Desk</div>
            <div className="text-[10px] text-zinc-600 leading-tight font-mono">Command Center</div>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 overflow-y-auto py-3 px-2 space-y-0.5">
        {sections.map((item, i) => {
          if ("divider" in item) {
            return <div key={i} className="h-px bg-border my-2 mx-2" />;
          }
          const Icon = item.icon;
          return (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === "/"}
              className={({ isActive }) =>
                clsx(
                  "flex items-center gap-2.5 px-2.5 py-1.5 rounded-md text-sm transition-colors",
                  isActive
                    ? "bg-violet-600/20 text-violet-400"
                    : "text-zinc-500 hover:text-zinc-300 hover:bg-surface-2"
                )
              }
            >
              <Icon size={14} />
              <span>{item.label}</span>
            </NavLink>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="px-4 py-3 border-t border-border">
        <p className="text-[10px] text-zinc-700 font-mono">v1.0.0 · local</p>
      </div>
    </aside>
  );
}
