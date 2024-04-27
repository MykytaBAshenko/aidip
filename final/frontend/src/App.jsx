import './App.css';
import { Route, Routes, BrowserRouter } from 'react-router-dom';
import Home from './views/home';
import MainWrapper from './layouts/MainWrapper';
import Login from './views/login';
import PrivateRoute from './layouts/PrivateRoute';
import Logout from './views/logout';
import Create from './views/create';
import List from './views/list';
import Order from './views/order';
import Register from './views/register';
import Header from './header';


function App() {
    return (

        <BrowserRouter>
            <Header />
            <MainWrapper>
                <Routes>
                    <Route
                        path="/create"
                        element={
                            <PrivateRoute>
                                <Create />
                            </PrivateRoute>
                        }
                    />
                    <Route
                        path="/list"
                        element={
                            <PrivateRoute>
                                <List />
                            </PrivateRoute>
                        }
                    />
                                        <Route
                        path="/order"
                        element={
                            <PrivateRoute>
                                <Order />
                            </PrivateRoute>
                        }
                    />
                    <Route path="/" element={<Home />} />
                    <Route path="/login" element={<Login />} />
                    <Route path="/register" element={<Register />} />
                    <Route path="/logout" element={<Logout />} />
                </Routes>
            </MainWrapper>
        </BrowserRouter>
    );
}

export default App;
