import React, { useEffect, useState } from 'react';
import styled from 'styled-components';
import api from '../api';

const GanttContainer = styled.div`
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  padding: 2rem;
  margin-bottom: 2rem;
`;

const GanttHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
`;

const GanttTitle = styled.h2`
  font-size: 1.5rem;
  color: #2c3e50;
`;

const BackButton = styled.button`
  display: flex;
  align-items: center;
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 0.5rem 1rem;
  font-size: 0.9rem;
  cursor: pointer;
  transition: background-color 0.2s;
  
  &:hover {
    background-color: #2980b9;
  }
  
  &:focus {
    outline: none;
    box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.5);
  }
`;

const GanttStats = styled.div`
  display: flex;
  gap: 1.5rem;
`;

const StatItem = styled.div`
  display: flex;
  align-items: center;
  font-size: 0.95rem;
`;

const StatLabel = styled.span`
  color: #7f8c8d;
  margin-right: 0.5rem;
`;

const StatValue = styled.span`
  font-weight: 600;
  color: #2c3e50;
`;

const GanttChartContainer = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  margin: 0 auto;
  overflow: auto;
`;

const GanttImage = styled.img`
  max-width: 100%;
  height: auto;
  margin: 0 auto;
  display: block;
`;

const LoadingContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
`;

const LoadingSpinner = styled.div`
  border: 4px solid rgba(0, 0, 0, 0.1);
  border-top: 4px solid #3498db;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

const LoadingMessage = styled.div`
  text-align: center;
  color: #7f8c8d;
  font-size: 1.2rem;
`;

const ErrorMessage = styled.div`
  text-align: center;
  padding: 3rem;
  color: #e74c3c;
  font-size: 1.2rem;
`;

const DemoModeTag = styled.div`
  display: inline-block;
  background-color: #f39c12;
  color: white;
  font-size: 0.8rem;
  font-weight: 600;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  margin-left: 1rem;
`;

interface GanttViewerProps {
  blockNumber: string;
  onBack?: () => void;
}

interface GanttData {
  block_number: string;
  image: string;
  node_count: number;
  edge_count: number;
  demo_mode: boolean;
}

const GanttViewer: React.FC<GanttViewerProps> = ({ blockNumber, onBack }) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [ganttData, setGanttData] = useState<GanttData | null>(null);

  useEffect(() => {
    const fetchGantt = async () => {
      setLoading(true);
      setError(null);
      
      try {
        const response = await api.get(`/gantt/${blockNumber}`);
        console.log('Gantt data received:', response.data);
        setGanttData(response.data);
      } catch (err: any) {
        console.error('Error fetching Gantt chart:', err);
        
        // Get more detailed error information
        const errorMessage = err.response?.data?.error || 'Failed to load Gantt chart. The block number may not exist or there was a server error.';
        setError(errorMessage);
      } finally {
        setLoading(false);
      }
    };

    fetchGantt();
  }, [blockNumber]);

  // Render the gantt chart image
  const renderGanttImage = () => {
    if (!ganttData?.image) {
      return <ErrorMessage>No chart image available</ErrorMessage>;
    }
    
    try {
      return (
        <GanttImage 
          src={`data:image/png;base64,${ganttData.image}`}
          alt={`Gantt chart for block ${blockNumber}`}
        />
      );
    } catch (error) {
      console.error('Error rendering Gantt image:', error);
      return <ErrorMessage>Error rendering the chart image</ErrorMessage>;
    }
  };

  return (
    <GanttContainer>
      <GanttHeader>
        <GanttTitle>
          Gantt Chart - Block #{ganttData?.block_number}
        </GanttTitle>
        <BackButton onClick={onBack}>
          &larr; Back to Recent Blocks
        </BackButton>
      </GanttHeader>
      
      <GanttStats>
        <StatItem>
          <StatLabel>Nodes:</StatLabel>
          <StatValue>{ganttData?.node_count}</StatValue>
        </StatItem>
        <StatItem>
          <StatLabel>Edges:</StatLabel>
          <StatValue>{ganttData?.edge_count}</StatValue>
        </StatItem>
        <StatItem>
          <StatLabel>View on:</StatLabel>
          <StatValue>
            <a 
              href={`https://beaconcha.in/block/${ganttData?.block_number}`} 
              target="_blank" 
              rel="noopener noreferrer"
              style={{ color: '#3498db', textDecoration: 'none' }}
            >
              beaconcha.in
            </a>
          </StatValue>
        </StatItem>
      </GanttStats>
      
      <GanttChartContainer>
        {loading ? (
          <LoadingContainer>
            <LoadingSpinner />
            <LoadingMessage>Loading Gantt chart for block {blockNumber}...</LoadingMessage>
          </LoadingContainer>
        ) : error ? (
          <ErrorMessage>{error}</ErrorMessage>
        ) : (
          renderGanttImage()
        )}
      </GanttChartContainer>
    </GanttContainer>
  );
};

export default GanttViewer; 