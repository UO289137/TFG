import React from 'react';
import { Navigate, Route, Routes } from 'react-router-dom';
import RootLayout from './layouts/RootLayout';
import Playground from './pages/Playground';
import Generator from './pages/Generator';

const App = () => {
  return (
    <Routes>
      {/* Rutas protegidas que usan el RootLayout */}
      <Route path="/" element={<RootLayout />}>
        {/* Ruta para Playground */}
        <Route path="/playground" element={<Playground />} />
        {/* Ruta para Generator */}
        <Route path="/generator" element={<Generator />} />
        {/* Ruta índice: si se accede a "/" redirige a "/playground" */}
        <Route index element={<Navigate to="/playground" replace />} />
      </Route>

      {/* Ruta de fallback para redirigir cualquier ruta no definida a Playground */}
      <Route path="*" element={<Navigate to="/playground" replace />} />
    </Routes>
  );
};

export default App;
