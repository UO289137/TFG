import React, { useEffect } from 'react';
import { Link, useLocation, useSearchParams } from 'react-router-dom';
import PlaygroundIcon from './Icons/PlaygroundIcon';
import GeneratorIcon from './Icons/GeneratorIcon';

const SideNavigation = () => {
  const location = useLocation();
  const pathname = location.pathname;
  const [searchParams] = useSearchParams();
  const model = searchParams.get('model');

  // Si entras a la raíz, se considerará activo el Playground
  const isPlaygroundActive = pathname === '/' || pathname === '/playground';
  const isGeneratorActive = pathname === '/generator';

  useEffect(() => {
    // Configuración de colores para cada ruta (se puede ampliar o ajustar)
    const backgroundColors = {
      '/generator': {
        body: '#C3278208', // Color de fondo para la ruta generator
        tab: '#FDF8FB',
      },
      '/playground': {
        body: '#ffffff',
        tab: '#ffffff',
      },
      '/': {
        body: '#ffffff',
        tab: '#ffffff',
      },
    };
    const { body: bodyBg, tab: tabBg } = backgroundColors[pathname] || {
      body: '#ffffff',
      tab: '#ffffff',
    };

    // Actualiza el color de fondo del body
    document.body.style.backgroundColor = bodyBg;

    // Actualiza el fondo de los elementos con la clase .vertical-rounded-tab
    const elements = document.querySelectorAll('.vertical-rounded-tab');
    elements.forEach((el) => {
      (el as HTMLElement).style.backgroundColor = tabBg;
    });

    // Configuración opcional: define una variable CSS según el modelo
    const modelColor =
      model === 'elixir'
        ? '#A077A8'
        : model === 'gold'
          ? '#1E647F'
          : model === 'ctgan'
            ? '#59B1FE'
            : '#C32782';
    document.documentElement.style.setProperty('--generator-color', modelColor);

    return () => {
      document.body.style.backgroundColor = '';
      elements.forEach((el) => {
        (el as HTMLElement).style.backgroundColor = '';
      });
      document.documentElement.style.removeProperty('--generator-color');
    };
  }, [pathname, model]);

  return (
    <nav className="w-64 lg:flex hidden h-screen flex-col justify-between sticky top-0 items-center rounded-[40px] bg-[#E3ECFF]">
      <div className="w-full relative z-50">
        <div className="p-4">
          <Link to="/playground">
            <img
              src="/logo-icon-transparent.png"
              alt="Logo"
              className="h-[75px] w-[75px] mx-auto object-contain pointer-events-none"
            />
          </Link>
        </div>
        <div className="w-full pl-8 z-50">
          {/* Elemento de navegación: Playground */}
          <div className="relative">
            <div
              className={`relative ${
                isPlaygroundActive
                  ? 'ml-[-4px] my-[-24px] vertical-rounded-tab -z-40'
                  : 'z-30'
              }`}
            >
              <Link
                to="/playground"
                className={`flex items-center py-2 gap-3 my-[5px] rounded-l-[30px] w-full text-sm px-4 ${
                  isPlaygroundActive
                    ? 'bg-gradient-to-r from-default to bg-white text-white'
                    : 'text-[#414042]'
                }`}
              >
                <PlaygroundIcon
                  className={`w-[16px] h-[16px] ${
                    isPlaygroundActive ? 'stroke-white' : 'stroke-[#414042]'
                  }`}
                />
                Playground
              </Link>
            </div>
          </div>

          {/* Divider */}
          <div className="line min-h-[1px] w-[80%] bg-gradient-to-r from-blue-600 to-transparent my-4"></div>

          {/* Elemento de navegación: El generador */}
          <div className="relative">
            <div
              className={`relative ${
                isGeneratorActive
                  ? 'ml-[-4px] my-[-24px] vertical-rounded-tab -z-40'
                  : 'z-30'
              }`}
            >
              <Link
                to="/generator?model=merlin"
                className={`flex items-center py-2 gap-3 my-[5px] rounded-l-[30px] w-full text-sm px-4 ${
                  isGeneratorActive
                    ? 'bg-gradient-to-r from-default to bg-white text-white'
                    : 'text-[#414042]'
                }`}
              >
                <GeneratorIcon
                  className={`w-[16px] h-[16px] ${
                    isGeneratorActive ? 'fill-white' : 'fill-[#414042]'
                  }`}
                />
                El generador
              </Link>
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default SideNavigation;
