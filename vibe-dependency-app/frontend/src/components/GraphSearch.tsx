import React, { useState } from 'react';
import styled from 'styled-components';

const SearchContainer = styled.div`
  margin-bottom: 2rem;
`;

const SearchForm = styled.form`
  display: flex;
  gap: 1rem;
  max-width: 600px;
  margin: 0 auto;
`;

const SearchInput = styled.input`
  flex: 1;
  padding: 0.75rem 1rem;
  border: 2px solid #ddd;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.3s;
  
  &:focus {
    outline: none;
    border-color: #3498db;
  }
`;

const SearchButton = styled.button`
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 0.75rem 1.5rem;
  font-weight: 600;
  transition: background-color 0.3s;
  
  &:hover {
    background-color: #2980b9;
  }
  
  &:focus {
    outline: none;
    box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.3);
  }
`;

interface GraphSearchProps {
  onSearch: (blockNumber: string) => void;
}

const GraphSearch: React.FC<GraphSearchProps> = ({ onSearch }) => {
  const [blockNumber, setBlockNumber] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (blockNumber.trim()) {
      onSearch(blockNumber.trim());
    }
  };

  return (
    <SearchContainer>
      <SearchForm onSubmit={handleSubmit}>
        <SearchInput 
          type="text" 
          placeholder="Enter Ethereum block number (e.g., 22195599)" 
          value={blockNumber}
          onChange={(e) => setBlockNumber(e.target.value)}
        />
        <SearchButton type="submit">Search</SearchButton>
      </SearchForm>
    </SearchContainer>
  );
};

export default GraphSearch; 