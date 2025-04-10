import React from 'react';
import { Outlet } from 'react-router-dom';
import SideNavigation from '../components/SideNavigation';
import Footer from '../components/Footer';

const RootLayout = () => {
  return (
    <div className={`lg:flex`}>
      <SideNavigation />
      <div className={`lg:flex-1 md:px-6 px-4 `}>
        <div className={`min-h-[calc(100vh-84px)] mb-8`}>
          <Outlet />
        </div>
        <Footer />
      </div>
    </div>
  );
};

export default RootLayout;
