import React from 'react';
import PlotlyComponent from 'react-plotly.js';

// Handle cases where Vite's CommonJS interop wraps the object inside `default`
const PlotComp = PlotlyComponent.default || PlotlyComponent;

export default function Plot(props) {
  return <PlotComp {...props} />;
}
