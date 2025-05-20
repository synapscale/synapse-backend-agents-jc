import React, { useState } from 'react';

type TooltipWrapperProps = {
  content: string;
  children: React.ReactNode;
};

const TooltipWrapper: React.FC<TooltipWrapperProps> = ({ content, children }) => {
  const [isVisible, setIsVisible] = useState(false);

  return (
    <div
      style={{ position: 'relative', display: 'inline-block' }}
      onMouseEnter={() => setIsVisible(true)}
      onMouseLeave={() => setIsVisible(false)}
    >
      {children}
      {isVisible && (
        <div
          style={{
            position: 'absolute',
            bottom: '100%',
            left: '50%',
            transform: 'translateX(-50%)',
            backgroundColor: 'black',
            color: 'white',
            padding: '5px',
            borderRadius: '3px',
            whiteSpace: 'nowrap',
            zIndex: 1000,
          }}
        >
          {content}
        </div>
      )}
    </div>
  );
};

export default TooltipWrapper;
