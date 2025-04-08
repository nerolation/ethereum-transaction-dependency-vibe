import React from 'react';
import styled from 'styled-components';

export type ViewType = 'graph' | 'gantt';

const ToggleContainer = styled.div`
  display: flex;
  justify-content: center;
  margin-bottom: 1.5rem;
`;

const ToggleButton = styled.button<{ isActive: boolean }>`
  background-color: ${props => props.isActive ? '#3498db' : '#ecf0f1'};
  color: ${props => props.isActive ? 'white' : '#7f8c8d'};
  font-weight: ${props => props.isActive ? '600' : '400'};
  padding: 0.6rem 1.2rem;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
  
  &:first-child {
    border-top-left-radius: 4px;
    border-bottom-left-radius: 4px;
  }
  
  &:last-child {
    border-top-right-radius: 4px;
    border-bottom-right-radius: 4px;
  }
  
  &:hover {
    background-color: ${props => props.isActive ? '#2980b9' : '#bdc3c7'};
  }
  
  &:focus {
    outline: none;
    box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.5);
  }
`;

interface ViewToggleProps {
  activeView: ViewType;
  onViewChange: (view: ViewType) => void;
}

const ViewToggle: React.FC<ViewToggleProps> = ({ activeView, onViewChange }) => {
  return (
    <ToggleContainer>
      <ToggleButton 
        isActive={activeView === 'graph'} 
        onClick={() => onViewChange('graph')}
      >
        Graph View
      </ToggleButton>
      <ToggleButton 
        isActive={activeView === 'gantt'} 
        onClick={() => onViewChange('gantt')}
      >
        Gantt View
      </ToggleButton>
    </ToggleContainer>
  );
};

export default ViewToggle; 