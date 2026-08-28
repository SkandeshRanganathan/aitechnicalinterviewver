import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './Home';
import Interview from './Interview';
import Summary from './Summary';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/interview/:sessionId" element={<Interview />} />
        <Route path="/summary/:sessionId" element={<Summary />} />
      </Routes>
    </Router>
  );
}

export default App;
