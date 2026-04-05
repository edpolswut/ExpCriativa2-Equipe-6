import React from "react";
import banner from '../img/banner.png';
import herois from '../img/herois.png';
import lendas from '../img/lendas.png';
import randall from '../img/randall.png';

function Main() {
  return (
    <main>
        <section className="hero">
        <img src={banner} alt="Banner"/>
        </section>

        <section className="carousel">
            <div className="carousel-container">
                <div className="card">
                    <img src={lendas}/>
                    <p>Loja de parafuso</p>
                </div>

                <div className="card">
                    <img src={randall}/>
                    <p>Site de Bet</p>
                </div>

                <div className="card">
                    <img src={herois}/>
                    <p>PUCPR</p>
                </div>
            </div>
        </section>
    </main>
  );
}

export default Main;