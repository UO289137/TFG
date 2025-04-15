import React from 'react';

const WelcomeScreen: React.FC = () => {
  const tfgPurpose =
    'Este Trabajo de Fin de Grado tiene como objetivo analizar y desarrollar soluciones innovadoras en el ámbito de la ingeniería, optimizando procesos y proponiendo mejoras estratégicas basadas en metodologías modernas. Aquí se abordarán tanto la parte teórica como la implementación práctica, garantizando una visión integral y profesional del proyecto.';

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100 p-4">
      <div className="bg-white shadow-md rounded-lg max-w-2xl w-full p-10">
        <header className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800">
            Bienvenido a mi TFG
          </h1>
        </header>
        <section className="mb-6">
          <div className="space-y-1 text-gray-700 text-lg">
            <p>
              <span className="font-semibold">Nombre:</span> Jaime Marín
              González
            </p>
            <p>
              <span className="font-semibold">UO:</span> UO289137
            </p>
            <p>
              <span className="font-semibold">DNI:</span> 53775258Q
            </p>
          </div>
        </section>
        <section className="mt-8">
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">
            Finalidad del TFG
          </h2>
          <p className="text-gray-700 leading-relaxed">{tfgPurpose}</p>
        </section>
      </div>
    </div>
  );
};

export default WelcomeScreen;
