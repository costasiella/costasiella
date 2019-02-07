// import React, { Component } from 'react';
// import logo from './logo.svg';
// import './App.css';


import React, { Component } from 'react'
import {Route, Switch, BrowserRouter} from 'react-router-dom'
import { ApolloProvider } from "react-apollo";
import ApolloClient from "apollo-boost";

import SchoolLocations from './components/SchoolLocations'
import NotFound from "./components/NotFound"
import './App.css'

const client = new ApolloClient({
     uri: "http://localhost:8000/graphql/"
});


class App extends Component {
  render() {
    return (
      <BrowserRouter>
        <ApolloProvider client={client}>
          <Switch>
            <Route exact path="/" component={SchoolLocations} />
            <Route component={NotFound} />
          </Switch>
        </ApolloProvider>
      </BrowserRouter>
    );
    }
}

export default App;



// import React from "react";
// import { render } from "react-dom";

// import { ApolloProvider } from "react-apollo";

// const App = () => (
//   <ApolloProvider client={client}>
//     <div>
//       <h2>My first Apollo app 🚀</h2>
//     </div>
//   </ApolloProvider>
// );

// render(<App />, document.getElementById("root"));







// class App extends Component {
//   render() {
//     return (
//       <div className="App">
//         <header className="App-header">
//           <img src={logo} className="App-logo" alt="logo" />
//           <p>
//             Edit <code>src/App.js</code> and save to reload.
//           </p>
//           <a
//             className="App-link"
//             href="https://reactjs.org"
//             target="_blank"
//             rel="noopener noreferrer"
//           >
//             Learn React 
//           </a>
//         </header>
//       </div>
//     );
//   }
// }

// export default App;
