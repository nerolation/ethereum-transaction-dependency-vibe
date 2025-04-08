import React, { useState } from 'react';
import styled from 'styled-components';

const SearchContainer = styled.div`
  margin-bottom: 2rem;
`;

const SearchForm = styled.form`
  display: flex;
  flex-direction: column;
  gap: 1rem;
  max-width: 600px;
  margin: 0 auto;
`;

const InputGroup = styled.div`
  display: flex;
  gap: 1rem;
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
  
  &:disabled {
    background-color: #95a5a6;
    cursor: not-allowed;
  }
`;

const ErrorMessage = styled.div`
  color: #e74c3c;
  font-size: 0.9rem;
  text-align: center;
  margin-top: 0.5rem;
`;

interface GraphSearchProps {
  onSearch: (blockNumber: string) => void;
}

const GraphSearch: React.FC<GraphSearchProps> = ({ onSearch }) => {
  const [blockNumber, setBlockNumber] = useState('');
  const [error, setError] = useState<string | null>(null);

  const validateBlockNumber = (value: string): boolean => {
    // Block number should be a positive integer
    if (!/^\d+$/.test(value)) {
      setError('Block number must be a positive integer');
      return false;
    }
    
    setError(null);
    return true;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmedValue = blockNumber.trim();
    
    if (!trimmedValue) {
      setError('Please enter a block number');
      return;
    }
    
    if (validateBlockNumber(trimmedValue)) {
      onSearch(trimmedValue);
    }
  };

  return (
    <SearchContainer>
      <SearchForm onSubmit={handleSubmit}>
        <InputGroup>
          <SearchInput 
            type="text" 
            placeholder="Enter Ethereum block number (e.g., 22195599)" 
            value={blockNumber}
            onChange={(e) => {
              setBlockNumber(e.target.value);
              if (error) validateBlockNumber(e.target.value);
            }}
          />
          <SearchButton 
            type="submit" 
            disabled={!blockNumber.trim()}
          >
            Search
          </SearchButton>
        </InputGroup>
        {error && <ErrorMessage>{error}</ErrorMessage>}
      </SearchForm>
    </SearchContainer>
  );
};

export default GraphSearch; 