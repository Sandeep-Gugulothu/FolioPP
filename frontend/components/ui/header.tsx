import Logo from "./logo";

export default function Header() {
  return (
    <header className="fixed top-2 z-30 w-full md:top-6">
      <div className="mx-auto max-w-6xl px-4 sm:px-6">
        <div className="relative flex h-14 items-center justify-between gap-3 rounded-2xl bg-white px-4 shadow-lg border border-gray-200">
          {/* Site branding */}
          <div className="flex items-center">
            <Logo />
          </div>

          {/* Site navigation & actions */}
          <nav className="flex flex-1 items-center justify-end gap-3 font-inter">
            <ul className="flex items-center gap-3">
              <li>
                <a
                  href="/signin"
                  className="btn-sm bg-white text-gray-800 shadow-sm hover:bg-gray-50 border border-gray-200"
                >
                  Login
                </a>
              </li>
              <li>
                <a
                  href="/signup"
                  className="btn-sm bg-blue-600 text-white shadow-sm hover:bg-blue-700 font-bold"
                >
                  Sign Up
                </a>
              </li>
            </ul>
          </nav>
        </div>
      </div>
    </header>
  );
}
