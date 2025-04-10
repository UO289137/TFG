/* eslint-disable @typescript-eslint/no-unused-vars */
import React, { Fragment, ReactNode, useState } from 'react';
import { cn } from '../utils/tailwindClassesMerge';
import { useLocation } from 'react-router-dom';

type Props = {
  containerClassName?: string;
  children?: ReactNode;
};

const TopBar: React.FC<Props> = ({ children, containerClassName }) => {
  const location = useLocation();
  const pathname = location.pathname;
  return (
    <Fragment>
      <nav
        className={cn(
          `lg:flex hidden justify-end items-center mb-4 pt-6 sticky top-0 z-[100] ${pathname.includes('/generator') ? '' : 'bg-white'}`,
          containerClassName
        )}
      >
        {children}
      </nav>
    </Fragment>
  );
};

export default TopBar;
