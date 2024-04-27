import Button from 'react-bootstrap/Button';
import Container from 'react-bootstrap/Container';
import Form from 'react-bootstrap/Form';
import Nav from 'react-bootstrap/Nav';
import Navbar from 'react-bootstrap/Navbar';
import NavDropdown from 'react-bootstrap/NavDropdown';
import Offcanvas from 'react-bootstrap/Offcanvas';
import { useAuthStore } from './store/auth';
import { useEffect, useState } from 'react';

function Header() {
    const [isLoggedIn, allUserData] = useAuthStore((state) => [
        state.isLoggedIn,
        state.allUserData,
    ]);
    useEffect(() => {
  }, [allUserData]);
  return (
    <>
      {[ 'md'].map((expand) => (
        <Navbar key={expand} expand={expand} className="navbar-dark bg-dark  mb-3">
          <Container fluid>
            <Navbar.Brand href="/">MILITARY AI OUTFIT</Navbar.Brand>
            <Navbar.Toggle aria-controls={`offcanvasNavbar-expand-${expand}`} />
            <Navbar.Offcanvas
              id={`offcanvasNavbar-expand-${expand}`}
              aria-labelledby={`offcanvasNavbarLabel-expand-${expand}`}
              placement="end"
            >
              <Offcanvas.Header closeButton>
                <Offcanvas.Title id={`offcanvasNavbarLabel-expand-${expand}`}>
                  Offcanvas
                </Offcanvas.Title>
              </Offcanvas.Header>
              <Offcanvas.Body>
                <Nav className="justify-content-end flex-grow-1 pe-3">
                {/* <NavDropdown
                    title="Dropdown"
                    id={`offcanvasNavbarDropdown-expand-${expand}`}
                  >
                    <NavDropdown.Item href="#action3">Action</NavDropdown.Item>
                    <NavDropdown.Item href="#action4">
                      Another action
                    </NavDropdown.Item>
                    <NavDropdown.Divider />
                    <NavDropdown.Item href="#action5">
                      Something else here
                    </NavDropdown.Item>
                  </NavDropdown> */}
                  {
                    allUserData ? <>
                      <Nav.Link href="/">Home</Nav.Link>
                      <Nav.Link href="/create">Create order</Nav.Link>
                      <Nav.Link href="/list">Orders list</Nav.Link>
                      <Nav.Link href="/logout">Logout</Nav.Link>
                    </> : <>
                      <Nav.Link href="/">Home</Nav.Link>
                      <Nav.Link href="/login">Login</Nav.Link>
                      <Nav.Link href="/register">Register</Nav.Link>
                    </>
                  }
                </Nav>
              </Offcanvas.Body>
            </Navbar.Offcanvas>
          </Container>
        </Navbar>
      ))}
    </>
  );
}

export default Header;