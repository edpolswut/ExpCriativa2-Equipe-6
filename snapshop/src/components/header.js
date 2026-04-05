import logo from '../img/logo.png';

function Header() {
  return (
    <header>
        <div className="left">
        <button className="logo">
        <img src={logo} alt="Página Principal" />
        </button>
    </div>

    <div className="center">
        <button>Sobre</button>
        <button>Contato</button>
    </div>

    <div className="right">
        <button>Entrar</button>
        <button>Criar conta</button>
    </div>
    </header>
  );
}

export default Header;