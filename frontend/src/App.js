import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Route, Routes, Navigate, Link } from 'react-router-dom';
import { Button, Container, AppBar, Toolbar, Typography, Box, IconButton, CssBaseline, ThemeProvider, Menu, MenuItem } from '@mui/material';
import ProductsList from './components/Product/ProductsList';
import ProductDetail from './components/Product/ProductDetail';
import StaffProductsList from './components/Product/StaffProductsList';
import UpdateProduct from './components/Product/UpdateProduct';
import WarehouseDetail from './components/Warehouse/WarehouseDetail';
import CategoriesList from './components/Category/CategoriesList';
import CategoryDetail from './components/Category/CategoryDetail';
import CreateCategory from './components/Category/CreateCategory';
import CreateWarehouse from './components/Warehouse/CreateWarehouse';
import WarehousesList from './components/Warehouse/WarehousesList';
import UsersList from './components/User/UsersList';
import ActivateAccount from './components/ActivateAccount';
import AllUsersList from './components/User/AllUsersList';
import CreateUser from './components/User/CreateUser';
import UserDetail from './components/User/UserDetail';
import AuthService from './services/AuthService';
import Login from './components/Login';
import CreateProduct from './components/Product/CreateProduct';
import NotFound from './components/NotFound';
import UserProfile from './components/User/UserProfile';
import './App.css';
import getTheme from './theme';

const App = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [isStaff, setIsStaff] = useState(false);
  const [themeMode, setThemeMode] = useState('light');
  const [anchorEl, setAnchorEl] = useState(null);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      setIsLoggedIn(true);
      setIsStaff(AuthService.getUserRole());
    }
  }, []);

  const handleLogin = async (email, password) => {
    try {
      await AuthService.login(email, password);
      setIsLoggedIn(true);
      setIsStaff(AuthService.getUserRole());
    } catch (error) {
      console.error("Login failed:", error);
    }
  };

  const handleLogout = () => {
    AuthService.logout();
    setIsLoggedIn(false);
    setIsStaff(false);
  };

  const toggleTheme = () => {
    setThemeMode((prevMode) => (prevMode === 'light' ? 'dark' : 'light'));
  };

  const handleMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  return (
    <ThemeProvider theme={getTheme(themeMode)}>
      <CssBaseline />
      <Router>
        <AppBar position="static" className={`app-bar ${themeMode}`}>
          <Toolbar>
            <Typography variant="h6" component={Link} to="/" sx={{ flexGrow: 1, textDecoration: 'none', color: 'inherit' }}>
              My App
            </Typography>
            {isLoggedIn && (
              <IconButton color="inherit" component={Link} to="/profile">
                <i className="fa fa-user" />
              </IconButton>
            )}
            <IconButton color="inherit" onClick={toggleTheme}>
              <i className={`fa fa-${themeMode === 'light' ? 'moon' : 'sun'}`} />
            </IconButton>
            {isLoggedIn ? (
              <>
                <Button color="inherit" onClick={handleLogout}>Logout</Button>
                <Button color="inherit" onClick={handleMenuOpen}>Menu</Button>
                <Menu
                  anchorEl={anchorEl}
                  open={Boolean(anchorEl)}
                  onClose={handleMenuClose}
                >
                  <MenuItem component={Link} to="/products">View Products</MenuItem>
                  <MenuItem component={Link} to="/categories">View Categories</MenuItem>
                  <MenuItem component={Link} to="/users">View Users</MenuItem>
                  <MenuItem component={Link} to="/warehouses">View Warehouse</MenuItem>
                  {isStaff && (
                    <>
                      <MenuItem component={Link} to="/products/all">Get All Products (Staff Only)</MenuItem>
                      <MenuItem component={Link} to="/users/all">Get All Users (Staff Only)</MenuItem>
                    </>
                  )}
                </Menu>
              </>
            ) : (
              <Button color="inherit" component={Link} to="/login">Login</Button>
            )}
          </Toolbar>
        </AppBar>
        <Container maxWidth="false" sx={{ mt: 4 }} className={`container ${themeMode}`}>
          <Routes>
            <Route
              path="/"
              element={
                isLoggedIn ? (
                  <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', mt: 4 }}>
                    <Button variant="contained" color="primary" component={Link} to="/products" sx={{ mb: 2 }}>
                      View Available Products
                    </Button>
                    <Button variant="contained" color="primary" component={Link} to="/categories" sx={{ mb: 2 }}>
                      View Categories
                    </Button>
                    <Button variant="contained" color="primary" component={Link} to="/users" sx={{ mb: 2 }}>
                      View Users
                    </Button>
                    <Button variant="contained" color="primary" component={Link} to="/warehouses" sx={{ mb: 2 }}>
                      View Warehouse
                    </Button>
                    {isStaff && (
                      <>
                        <Button variant="contained" color="secondary" component={Link} to="/products/all" sx={{ mb: 2 }}>
                          Get All Products (Staff Only)
                        </Button>
                        <Button variant="contained" color="secondary" component={Link} to="/users/all" sx={{ mb: 2 }}>
                          Get All Users (Staff Only)
                        </Button>
                      </>
                    )}
                  </Box>
                ) : (
                  <Login handleLogin={handleLogin} />
                )
              }
            />
            <Route path="/login" element={isLoggedIn ? <Navigate to="/" /> : <Login handleLogin={handleLogin} />} />
            <Route path="/products" element={isLoggedIn ? <ProductsList themeMode={themeMode} /> : <Navigate to="/login" />} />
            <Route path="/product/:productId" element={isLoggedIn ? <ProductDetail themeMode={themeMode} /> : <Navigate to="/login" />} />
            <Route path="/product/create" element={isLoggedIn ? <CreateProduct themeMode={themeMode} /> : <Navigate to="/login" />} />
            <Route
              path="/products/all"
              element={
                isLoggedIn && isStaff ? (
                  <StaffProductsList themeMode={themeMode} />
                ) : (
                  <Navigate to={isLoggedIn ? "/" : "/login"} />
                )
              }
            />
            <Route
              path="/product/update/:productId"
              element={
                isLoggedIn && isStaff ? (
                  <UpdateProduct themeMode={themeMode} />
                ) : (
                  <Navigate to={isLoggedIn ? "/" : "/login"} />
                )
              }
            />
            <Route path="/categories" element={isLoggedIn ? <CategoriesList themeMode={themeMode} /> : <Navigate to="/login" />} />
            <Route path="/category/:categoryId" element={isLoggedIn ? <CategoryDetail themeMode={themeMode} /> : <Navigate to="/login" />} />
            <Route path="/category/create" element={isLoggedIn ? <CreateCategory themeMode={themeMode} /> : <Navigate to="/login" />} />
            <Route
              path="/users"
              element={
                isLoggedIn ? (
                  <UsersList themeMode={themeMode} />
                ) : (
                  <Navigate to="/login" />
                )
              }
            />
            <Route path="/user/create" element={isLoggedIn && isStaff ? <CreateUser themeMode={themeMode} /> : <Navigate to={isLoggedIn ? "/users/all" : "/login"} />} />
            <Route path="/user/:userId" element={isLoggedIn ? <UserDetail themeMode={themeMode} /> : <Navigate to="/login" />} />
            <Route path="/users/all" element={isLoggedIn && isStaff ? <AllUsersList themeMode={themeMode} /> : <Navigate to="/" />} />
            <Route path="/profile" element={isLoggedIn ? <UserProfile themeMode={themeMode} /> : <Navigate to="/login" />} />
            <Route path="/activate-account/:token" element={<ActivateAccount />} />
            <Route
              path="/warehouses"
              element={isLoggedIn ? <WarehousesList themeMode={themeMode} /> : <Navigate to="/login" />}
            />
            <Route
              path="/warehouse/create"
              element={isLoggedIn && isStaff ? <CreateWarehouse themeMode={themeMode} /> : <Navigate to="/" />}
            />
            <Route
              path="/warehouse/:warehouseId"
              element={isLoggedIn ? <WarehouseDetail themeMode={themeMode} /> : <Navigate to="/login" />}
            />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </Container>
      </Router>
    </ThemeProvider>
  );
};

export default App;
