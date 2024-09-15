  import React, { useState, useEffect } from 'react';
  import { BrowserRouter as Router, Route, Routes, Navigate, Link } from 'react-router-dom';
  import { Button, Container, AppBar, Toolbar, Typography, Box, IconButton, CssBaseline, ThemeProvider, Menu, MenuItem } from '@mui/material';
  import ProductsList from './components/Product/ProductsList';
  import ProductDetail from './components/Product/ProductDetail';
  import StaffProductsList from './components/Product/StaffProductsList';
  import UpdateProduct from './components/Product/UpdateProduct';
  import WarehouseDetail from './components/Warehouse/WarehouseDetail';
  import WaitingRoomDetail from './components/WaitingRoom/WaitingRoomDetail';
  import UpdateWaitingRoom from './components/WaitingRoom/UpdateWaitingRoom';
  import UpdateWarehouse from './components/Warehouse/UpdateWarehouse';
  import CategoriesList from './components/Category/CategoriesList';
  import CategoryDetail from './components/Category/CategoryDetail';
  import CreateCategory from './components/Category/CreateCategory';
  import CreateWarehouse from './components/Warehouse/CreateWarehouse';
  import WaitingRoomsList from './components/WaitingRoom/WaitingRoomsList';
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
  import CreateWaitingRoom from './components/WaitingRoom/CreateWaitingRoom';
  import CreateReception from './components/Reception/CreateReception';
  import ReceptionsList from './components/Reception/ReceptionsList';
  import ReceptionDetail from './components/Reception/ReceptionDetail';
  import StocksList from './components/Stock/StocksList';
  import StockDetail from './components/Stock/StockDetail';
  import AllStocksList from './components/Stock/AllStocksList';
  import AllStockDetail from './components/Stock/AllStockDetail';
  import CreateIssue from './components/Issue/CreateIssue';
  import IssueList from './components/Issue/IssueList';
  import IssueDetail from './components/Issue/IssueDetail';
  import CreateSection from './components/Section/CreateSection';
  import SectionsList from './components/Section/SectionsList';
  import SectionDetail from './components/Section/SectionDetail';
  import UpdateSection from './components/Section/UpdateSection';
  import CreateRack from './components/Rack/CreateRack';
  import RacksList from './components/Rack/RacksList';
  import RackDetail from './components/Rack/RackDetail';
  import UpdateRack from './components/Rack/UpdateRack';
  import CreateRackLevel from './components/RackLevel/CreateRackLevel';
  import RackLevelsList from './components/RackLevel/RackLevelsList';
  import RackLevelDetail from './components/RackLevel/RackLevelDetail';
  import UpdateRackLevel from './components/RackLevel/UpdateRackLevel';
  import RackLevelSlotsList from './components/RackLevelSlot/RackLevelSlotsList';
  import RackLevelSlotDetail from './components/RackLevelSlot/RackLevelSlotDetail';
  import UpdateRackLevelSlot from './components/RackLevelSlot/UpdateRackLevelSlot';
  import './App.css';
  import getTheme from './theme';

  const App = () => {
    const [isLoggedIn, setIsLoggedIn] = useState(false);
    const [isStaff, setIsStaff] = useState(false);
    const [canReceptStocks, setCanReceptStocks] = useState(false);
    const [canMoveStocks, setCanMoveStocks] = useState(false);
    const [canIssueStocks, setCanIssueStocks] = useState(false);
    const [themeMode, setThemeMode] = useState('light');
    const [anchorEl, setAnchorEl] = useState(null);

    useEffect(() => {
      const token = localStorage.getItem('token');
      if (token) {
        setIsLoggedIn(true);
        setIsStaff(AuthService.getUserRole());
        setCanReceptStocks(AuthService.canReceptStocks());
        setCanMoveStocks(AuthService.canMoveStocks());
        setCanIssueStocks(AuthService.canIssueStocks());
      }
    }, []);

    const handleLogin = async (email, password) => {
      try {
        await AuthService.login(email, password);
        setIsLoggedIn(true);
        setIsStaff(AuthService.getUserRole());
        setCanReceptStocks(AuthService.canReceptStocks());
        setCanMoveStocks(AuthService.canMoveStocks());
        setCanIssueStocks(AuthService.canIssueStocks());
      } catch (error) {
        console.error("Login failed:", error);
      }
    };

    const handleLogout = () => {
      AuthService.logout();
      setIsLoggedIn(false);
      setIsStaff(false);
      setCanReceptStocks(false);
      setCanMoveStocks(false);
      setCanIssueStocks(false);
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
                    <MenuItem component={Link} to="/waiting_rooms">View Waiting Rooms</MenuItem>
                    <MenuItem component={Link} to="/stocks">View Available Stocks</MenuItem>
                    <MenuItem component={Link} to="/sections">View Sections</MenuItem>
                    <MenuItem component={Link} to="/racks">View Racks</MenuItem>
                    <MenuItem component={Link} to="/rack-levels">View Rack Levels</MenuItem>
                    <MenuItem component={Link} to="/rack-level-slots">View Rack Level Slots</MenuItem>
                    {(canReceptStocks || isStaff) && (
                      <>
                      <MenuItem component={Link} to="/receptions">View Receptions</MenuItem>
                      </>
                    )}
                    {(canIssueStocks || isStaff) && (
                      <>
                      <MenuItem component={Link} to="/issues">View Issues</MenuItem>
                      </>
                    )}
                    {isStaff && (
                      <>
                        <MenuItem component={Link} to="/products/all">Get All Products (Staff Only)</MenuItem>
                        <MenuItem component={Link} to="/users/all">Get All Users (Staff Only)</MenuItem>
                        <MenuItem component={Link} to="/stocks/all">Get All Stocks (Staff Only)</MenuItem>
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
                      <Button variant="contained" color="primary" component={Link} to="/waiting_rooms" sx={{ mb: 2 }}>
                        View Waiting Rooms
                      </Button>
                      <Button variant="contained" color="primary" component={Link} to="/stocks" sx={{ mb: 2 }}>
                        View Available Stocks
                      </Button>
                      <Button variant="contained" color="primary" component={Link} to="/sections" sx={{ mb: 2 }}>
                        View Sections
                      </Button>
                      <Button variant="contained" color="primary" component={Link} to="/racks" sx={{ mb: 2 }}>
                        View Racks
                      </Button>
                      <Button variant="contained" color="primary" component={Link} to="/rack-levels" sx={{ mb: 2 }}>
                        View Rack Levels
                      </Button>
                      <Button variant="contained" color="primary" component={Link} to="/rack-level-slots" sx={{ mb: 2 }}>
                        View Rack Level Slots
                      </Button>
                      {(canReceptStocks || isStaff) && (
                      <Button variant="contained" color="secondary" component={Link} to="/receptions" sx={{ mb: 2 }}>
                        View Receptions
                      </Button>
                      )}
                      {(canIssueStocks || isStaff) && (
                      <Button variant="contained" color="secondary" component={Link} to="/issues" sx={{ mb: 2 }}>
                        View Issues
                      </Button>
                      )}
                      {isStaff && (
                        <>
                          <Button variant="contained" color="secondary" component={Link} to="/products/all" sx={{ mb: 2 }}>
                            Get All Products (Staff Only)
                          </Button>
                          <Button variant="contained" color="secondary" component={Link} to="/users/all" sx={{ mb: 2 }}>
                            Get All Users (Staff Only)
                          </Button>
                          <Button variant="contained" color="secondary" component={Link} to="/stocks/all" sx={{ mb: 2 }}>
                            Get All Stocks (Staff Only)
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
              <Route
                path="/users/all"
                element={
                  isLoggedIn && isStaff ? (
                    <AllUsersList themeMode={themeMode} />
                  ) : (
                    <Navigate to={isLoggedIn ? "/" : "/login"} />
                  )
                }
              />
              <Route path="/warehouses" element={isLoggedIn ? <WarehousesList themeMode={themeMode} /> : <Navigate to="/login" />} />
              <Route path="/warehouse/create" element={isLoggedIn && isStaff ? <CreateWarehouse themeMode={themeMode} /> : <Navigate to="/login" />} />
              <Route path="/warehouse/:warehouseId" element={isLoggedIn ? <WarehouseDetail themeMode={themeMode} /> : <Navigate to="/login" />} />
              <Route path="/warehouse/update/:warehouseId" element={isLoggedIn && isStaff ? <UpdateWarehouse themeMode={themeMode} /> : <Navigate to="/login" />} />
              <Route path="/waiting_rooms" element={isLoggedIn ? <WaitingRoomsList themeMode={themeMode} /> : <Navigate to="/login" />} />
              <Route path="/waiting_room/create" element={isLoggedIn ? <CreateWaitingRoom themeMode={themeMode} /> : <Navigate to="/login" />} />
              <Route path="/waiting_room/:waitingRoomId" element={isLoggedIn ? <WaitingRoomDetail themeMode={themeMode} /> : <Navigate to="/login" />} />
              <Route path="/waiting_room/update/:waitingRoomId" element={isLoggedIn && isStaff ? <UpdateWaitingRoom themeMode={themeMode} /> : <Navigate to="/login" />} />
              <Route path="/activate/:token" element={isLoggedIn ? <ActivateAccount /> : <Navigate to="/login" />} />
              <Route path="/profile" element={isLoggedIn ? <UserProfile themeMode={themeMode} /> : <Navigate to="/login" />} />
              <Route path="/reception/create" element={isLoggedIn || canReceptStocks ? <CreateReception themeMode={themeMode} /> : <Navigate to={isLoggedIn ? "/" : "/login"} />} />
              <Route path="/receptions" element={isLoggedIn && (canReceptStocks || canMoveStocks) ? <ReceptionsList themeMode={themeMode} /> : <Navigate to={isLoggedIn ? "/" : "/login"} />} />
              <Route path="/reception/:receptionId" element={isLoggedIn && canReceptStocks ? <ReceptionDetail themeMode={themeMode} /> : <Navigate to={isLoggedIn ? "/" : "/login"} />} />
              <Route path="/stocks" element={isLoggedIn ? <StocksList themeMode={themeMode} /> : <Navigate to="/login" />} />
              <Route path="/stock/:stockId" element={isLoggedIn ? <StockDetail themeMode={themeMode} /> : <Navigate to="/login" />} />
              <Route path="/stocks/all" element={isLoggedIn && isStaff ? <AllStocksList themeMode={themeMode} /> : <Navigate to="/login" />} />
              <Route path="/stock/all/:stockId" element={isLoggedIn && isStaff ? <AllStockDetail themeMode={themeMode} /> : <Navigate to="/login" />} />
              <Route path="/issue/create" element={isLoggedIn && canIssueStocks ? <CreateIssue themeMode={themeMode} /> : <Navigate to={isLoggedIn ? "/" : "/login"} />} />
              <Route path="/issues" element={isLoggedIn && (canIssueStocks || canMoveStocks) ? <IssueList themeMode={themeMode} /> : <Navigate to={isLoggedIn ? "/" : "/login"} />} />
              <Route path="/issue/:issueId" element={isLoggedIn && canIssueStocks ? <IssueDetail themeMode={themeMode} /> : <Navigate to="/login" />} />
              <Route path="*" element={<NotFound themeMode={themeMode} />} />
              <Route path="/section/create" element={isLoggedIn && isStaff ? <CreateSection themeMode={themeMode} /> : <Navigate to="/login" />} />
              <Route path="/sections" element={isLoggedIn ? <SectionsList themeMode={themeMode} /> : <Navigate to="/login" />} />
              <Route path="/section/:sectionId" element={isLoggedIn ? <SectionDetail themeMode={themeMode} /> : <Navigate to="/login" />} />
              <Route path="/section/:sectionId/update" element={isLoggedIn && isStaff ? <UpdateSection themeMode={themeMode} /> : <Navigate to="/login" />} />
              <Route path="/rack/create" element={isLoggedIn && isStaff ? <CreateRack themeMode={themeMode} /> : <Navigate to="/login" />} />
              <Route path="/racks" element={isLoggedIn ? <RacksList themeMode={themeMode} /> : <Navigate to="/login" />} />
              <Route path="/rack/:rackId" element={isLoggedIn ? <RackDetail themeMode={themeMode} /> : <Navigate to="/login" />} />
              <Route path="/rack/:rackId/update" element={isLoggedIn && isStaff ? <UpdateRack themeMode={themeMode} /> : <Navigate to="/login" />} />
              <Route path="/rack-level/create" element={isLoggedIn && isStaff ? <CreateRackLevel themeMode={themeMode} /> : <Navigate to="/login" />} />
              <Route path="/rack-levels" element={isLoggedIn ? <RackLevelsList themeMode={themeMode} /> : <Navigate to="/login" />} />
              <Route path="/rack-level/:rackLevelId" element={isLoggedIn ? <RackLevelDetail themeMode={themeMode} /> : <Navigate to="/login" />} />
              <Route path="/rack-level/:rackLevelId/update" element={isLoggedIn && isStaff ? <UpdateRackLevel themeMode={themeMode} /> : <Navigate to="/login" />} />
              <Route path="/rack-level-slots" element={isLoggedIn ? <RackLevelSlotsList themeMode={themeMode} /> : <Navigate to="/login" />} />
              <Route path="/rack-level-slot/:rackLevelSlotId" element={isLoggedIn ? <RackLevelSlotDetail themeMode={themeMode} /> : <Navigate to="/login" />} />
              <Route path="/rack-level-slot/:rackLevelSlotId/update" element={isLoggedIn ? <UpdateRackLevelSlot themeMode={themeMode} /> : <Navigate to="/login" />} />
              </Routes>
          </Container>
        </Router>
      </ThemeProvider>
    );
  };

  export default App;
