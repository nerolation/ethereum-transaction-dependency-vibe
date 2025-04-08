declare module 'react-plotly.js' {
  import * as Plotly from 'plotly.js';
  import * as React from 'react';

  interface PlotParams {
    data: Plotly.Data[];
    layout: Partial<Plotly.Layout>;
    frames?: Plotly.Frame[];
    config?: Partial<Plotly.Config>;
    useResizeHandler?: boolean;
    style?: React.CSSProperties;
    className?: string;
    onInitialized?: (figure: Plotly.Figure, graphDiv: HTMLElement) => void;
    onUpdate?: (figure: Plotly.Figure, graphDiv: HTMLElement) => void;
    onPurge?: (figure: Plotly.Figure, graphDiv: HTMLElement) => void;
    onError?: (err: Error) => void;
    onClick?: (event: Plotly.PlotMouseEvent) => void;
    onClickAnnotation?: (event: Plotly.PlotMouseEvent) => void;
    onBeforeHover?: (event: Plotly.PlotMouseEvent) => void;
    onHover?: (event: Plotly.PlotMouseEvent) => void;
    onUnhover?: (event: Plotly.PlotMouseEvent) => void;
    onSelected?: (event: Plotly.PlotSelectionEvent) => void;
    onDeselect?: (event: Plotly.PlotSelectionEvent) => void;
    onDoubleClick?: (event: Plotly.PlotMouseEvent) => void;
    onRelayout?: (event: Plotly.PlotRelayoutEvent) => void;
    onRestyle?: (event: Plotly.PlotRestyleEvent) => void;
    onReveal?: (event: Plotly.PlotSelectionEvent) => void;
    onSliderChange?: (event: Plotly.PlotSliderChangeEvent) => void;
    onSliderEnd?: (event: Plotly.PlotSliderEndEvent) => void;
    onSliderStart?: (event: Plotly.PlotSliderStartEvent) => void;
    onAnimated?: () => void;
    onAnimatingFrame?: (event: { name: string; frame: Plotly.Frame }) => void;
    onAfterExport?: () => void;
    onAfterPlot?: () => void;
    onBeforeExport?: () => void;
    onAddTrace?: () => void;
    onRedraw?: () => void;
    onWebGlContextLost?: () => void;
    [key: string]: any;
  }

  class Plot extends React.Component<PlotParams> {}
  export default Plot;
} 