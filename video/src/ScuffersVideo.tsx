import React from 'react';
import {
  AbsoluteFill,
  Sequence,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
  Img,
  staticFile,
} from 'remotion';
import { loadFont } from '@remotion/google-fonts/Inter';

const { fontFamily } = loadFont();

export const FPS = 30;
export const WIDTH = 1920;
export const HEIGHT = 1080;

// Scene durations in seconds
const S = {
  s1: 3,
  s2: 5,
  s3: 7,
  s4: 7,
  s5: 10,
  s6: 10,
  s7: 8,
  s8: 8,
  s9: 10,
  s10: 7,
};

const f = (sec: number) => Math.round(sec * FPS);
const starts = (() => {
  let t = 0;
  const out: Record<string, number> = {};
  for (const [k, v] of Object.entries(S)) {
    out[k] = t;
    t += v as number;
  }
  return out;
})();
export const TOTAL_DURATION = f(Object.values(S).reduce((a, b) => a + b, 0));

// Colors
const C = {
  bg: '#FFFFFF',
  green: '#2B7551',
  text: '#111111',
  red: '#C43232',
  amber: '#B8801F',
  softRed: '#FBE9E9',
  softGreen: '#E5F2EC',
  gray: '#7A7A7A',
  border: '#EAEAEA',
};

const baseStyle: React.CSSProperties = {
  fontFamily,
  backgroundColor: C.bg,
  color: C.text,
};

// helpers
const useFade = (from: number, dur = 15) => {
  const frame = useCurrentFrame();
  return interpolate(frame, [from, from + dur], [0, 1], { extrapolateRight: 'clamp', extrapolateLeft: 'clamp' });
};

const useFadeOut = (start: number, dur = 8) => {
  const frame = useCurrentFrame();
  return interpolate(frame, [start, start + dur], [1, 0], { extrapolateRight: 'clamp', extrapolateLeft: 'clamp' });
};

// =================== Scene 1: Logo intro ===================
const Scene1: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const op = spring({ frame, fps, config: { damping: 200 } });
  const subOp = interpolate(frame, [15, 35], [0, 1], { extrapolateRight: 'clamp' });
  const tagOp = interpolate(frame, [25, 45], [0, 1], { extrapolateRight: 'clamp' });
  return (
    <AbsoluteFill style={{ ...baseStyle, justifyContent: 'center', alignItems: 'center' }}>
      <div style={{ opacity: op, transform: `scale(${0.9 + op * 0.1})` }}>
        <Img src={staticFile('scuffers_logo.png')} style={{ width: 360, height: 'auto' }} />
      </div>
      <div style={{
        opacity: subOp,
        marginTop: 40,
        fontSize: 72,
        fontWeight: 800,
        fontStyle: 'italic',
        color: C.green,
        letterSpacing: -2,
      }}>
        Drop Co-Pilot
      </div>
      <div style={{ opacity: tagOp, marginTop: 28, fontSize: 22, color: C.gray, letterSpacing: 6, fontWeight: 600 }}>
        UDIA × ESIC HACKATHON 2026
      </div>
    </AbsoluteFill>
  );
};

// =================== Scene 2: El problema ===================
const Scene2: React.FC = () => {
  const frame = useCurrentFrame();
  const titleOp = interpolate(frame, [0, 15], [0, 1], { extrapolateRight: 'clamp' });
  const stats = [
    { label: '180 pedidos', t: 20 },
    { label: '12 incidencias', t: 35 },
    { label: '8 VIPs en riesgo', t: 50 },
    { label: '€11.823 en juego', t: 65, accent: true },
  ];
  const finalOp = interpolate(frame, [95, 115], [0, 1], { extrapolateRight: 'clamp' });
  return (
    <AbsoluteFill style={{ ...baseStyle, padding: 120, justifyContent: 'center' }}>
      <div style={{
        opacity: titleOp,
        transform: `translateY(${(1 - titleOp) * 20}px)`,
        fontSize: 110,
        fontWeight: 900,
        fontStyle: 'italic',
        letterSpacing: -4,
        marginBottom: 50,
      }}>
        16:00 · Drop activo
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
        {stats.map((s, i) => {
          const op = interpolate(frame, [s.t, s.t + 12], [0, 1], { extrapolateRight: 'clamp' });
          return (
            <div key={i} style={{
              opacity: op,
              transform: `translateX(${(1 - op) * -30}px)`,
              fontSize: 56,
              fontWeight: 800,
              color: s.accent ? C.red : C.text,
              borderLeft: `6px solid ${s.accent ? C.red : C.green}`,
              paddingLeft: 28,
            }}>
              {s.label}
            </div>
          );
        })}
      </div>
      <div style={{
        opacity: finalOp,
        marginTop: 50,
        fontSize: 38,
        fontWeight: 700,
        color: C.gray,
        fontStyle: 'italic',
      }}>
        El equipo necesita decidir AHORA.
      </div>
    </AbsoluteFill>
  );
};

// =================== Scene 3: Health Score ===================
const Scene3: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const labelOp = interpolate(frame, [0, 15], [0, 1], { extrapolateRight: 'clamp' });
  const numProgress = spring({ frame: frame - 10, fps, config: { damping: 18, stiffness: 90 } });
  const value = Math.round(numProgress * 69);
  const subOp = interpolate(frame, [60, 80], [0, 1], { extrapolateRight: 'clamp' });
  const phraseOp = interpolate(frame, [100, 130], [0, 1], { extrapolateRight: 'clamp' });
  return (
    <AbsoluteFill style={{ ...baseStyle, justifyContent: 'center', alignItems: 'center' }}>
      <div style={{ opacity: labelOp, fontSize: 26, letterSpacing: 12, color: C.gray, fontWeight: 700 }}>
        DROP HEALTH
      </div>
      <div style={{
        fontSize: 380,
        fontWeight: 900,
        fontStyle: 'italic',
        color: C.amber,
        letterSpacing: -16,
        lineHeight: 1,
        marginTop: 10,
        transform: `scale(${0.6 + numProgress * 0.4})`,
      }}>
        {value}
      </div>
      <div style={{ opacity: subOp, fontSize: 38, fontWeight: 700, color: C.amber, marginTop: -10, letterSpacing: 4 }}>
        / 100 · ATENCIÓN
      </div>
      <div style={{ opacity: phraseOp, marginTop: 60, fontSize: 36, fontStyle: 'italic', color: C.text, fontWeight: 600 }}>
        Una sola cifra. Decisión instantánea.
      </div>
    </AbsoluteFill>
  );
};

// =================== Scene 4: Counterfactual Twin ===================
const Scene4: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const titleOp = interpolate(frame, [0, 15], [0, 1], { extrapolateRight: 'clamp' });
  const leftOp = interpolate(frame, [15, 35], [0, 1], { extrapolateRight: 'clamp' });
  const rightOp = interpolate(frame, [30, 55], [0, 1], { extrapolateRight: 'clamp' });
  const banner = interpolate(frame, [85, 110], [0, 1], { extrapolateRight: 'clamp' });

  const sp1 = spring({ frame: frame - 15, fps, config: { damping: 20 } });
  const left = Math.round(sp1 * 3375);
  const sp2 = spring({ frame: frame - 30, fps, config: { damping: 20 } });
  const right = Math.round(sp2 * 169);

  return (
    <AbsoluteFill style={{ ...baseStyle, padding: 60, justifyContent: 'center' }}>
      <div style={{
        opacity: titleOp,
        textAlign: 'center',
        fontSize: 64,
        fontWeight: 900,
        letterSpacing: -2,
        marginBottom: 40,
      }}>
        ¿QUÉ PASA SI NO ACTUAMOS?
      </div>
      <div style={{ display: 'flex', gap: 30, height: 600 }}>
        <div style={{
          flex: 1,
          background: C.softRed,
          borderRadius: 16,
          padding: 50,
          opacity: leftOp,
          transform: `translateX(${(1 - leftOp) * -40}px)`,
          display: 'flex', flexDirection: 'column', justifyContent: 'center',
        }}>
          <div style={{ fontSize: 28, fontWeight: 800, letterSpacing: 6, color: C.red, marginBottom: 20 }}>SIN ACTUAR</div>
          <div style={{ fontSize: 140, fontWeight: 900, fontStyle: 'italic', color: C.red, letterSpacing: -6, lineHeight: 1 }}>
            -€{left.toLocaleString('es-ES')}
          </div>
          <div style={{ fontSize: 30, fontWeight: 600, color: C.text, marginTop: 24 }}>
            34 oversells · 2 VIPs heridos
          </div>
        </div>
        <div style={{
          flex: 1,
          background: C.softGreen,
          borderRadius: 16,
          padding: 50,
          opacity: rightOp,
          transform: `translateX(${(1 - rightOp) * 40}px)`,
          display: 'flex', flexDirection: 'column', justifyContent: 'center',
        }}>
          <div style={{ fontSize: 28, fontWeight: 800, letterSpacing: 6, color: C.green, marginBottom: 20 }}>CON PLAN</div>
          <div style={{ fontSize: 140, fontWeight: 900, fontStyle: 'italic', color: C.green, letterSpacing: -6, lineHeight: 1 }}>
            -€{right.toLocaleString('es-ES')}
          </div>
          <div style={{ fontSize: 30, fontWeight: 600, color: C.text, marginTop: 24 }}>
            0 oversells · 0 VIPs heridos
          </div>
        </div>
      </div>
      <div style={{
        opacity: banner,
        marginTop: 30,
        background: C.text,
        color: C.green,
        padding: '30px 50px',
        borderRadius: 12,
        textAlign: 'center',
        fontSize: 72,
        fontWeight: 900,
        fontStyle: 'italic',
        letterSpacing: -2,
      }}>
        +€3.206 SALVADOS
      </div>
    </AbsoluteFill>
  );
};

// =================== Scene 5: Top 10 acciones ===================
const Scene5: React.FC = () => {
  const frame = useCurrentFrame();
  const titleOp = interpolate(frame, [0, 15], [0, 1], { extrapolateRight: 'clamp' });
  const cards = [
    { num: '01', title: 'Pausar campaña Tiktok', desc: 'Madrid · Black Hoodie M', val: '€1.684 recuperables' },
    { num: '02', title: 'Bloquear venta', desc: 'Black Zip Hoodie M', val: '€1.010 · 1 VIP' },
    { num: '03', title: 'Escalar a humano', desc: 'Ticket urgente VIP CUS-2033', val: 'LTV €2.119' },
    { num: '08', title: 'Contactar VIP', desc: 'Mensaje listo para CUS-2033', val: '«Qué pasa, CUS-2033...»' },
  ];
  // each card visible for ~60 frames
  const perCard = 60;
  return (
    <AbsoluteFill style={{ ...baseStyle, padding: 120, justifyContent: 'center' }}>
      <div style={{
        opacity: titleOp,
        fontSize: 72,
        fontWeight: 900,
        letterSpacing: -3,
        marginBottom: 50,
      }}>
        10 ACCIONES PRIORIZADAS
      </div>
      <div style={{ position: 'relative', height: 240 }}>
        {cards.map((c, i) => {
          const start = 20 + i * perCard;
          const op = interpolate(frame, [start, start + 15, start + perCard - 5, start + perCard + 15],
            [0, 1, 1, 0], { extrapolateRight: 'clamp', extrapolateLeft: 'clamp' });
          const slide = interpolate(frame, [start, start + 15], [40, 0], { extrapolateRight: 'clamp', extrapolateLeft: 'clamp' });
          return (
            <div key={i} style={{
              position: 'absolute',
              top: 0, left: 0, right: 0,
              opacity: op,
              transform: `translateY(${slide}px)`,
              background: '#FFFFFF',
              border: `1px solid ${C.border}`,
              borderLeft: `8px solid ${C.green}`,
              borderRadius: 8,
              padding: '40px 50px',
              display: 'flex',
              alignItems: 'center',
              gap: 50,
              boxShadow: '0 8px 30px rgba(0,0,0,0.06)',
            }}>
              <div style={{ fontSize: 130, fontWeight: 900, fontStyle: 'italic', color: C.green, letterSpacing: -6, lineHeight: 1, minWidth: 200 }}>
                #{c.num}
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: 48, fontWeight: 800, marginBottom: 10 }}>{c.title}</div>
                <div style={{ fontSize: 28, color: C.gray, marginBottom: 6 }}>{c.desc}</div>
                <div style={{ fontSize: 30, fontWeight: 700, color: C.text }}>{c.val}</div>
              </div>
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

// =================== Scene 6: Telegram ===================
const Scene6: React.FC = () => {
  const frame = useCurrentFrame();
  const titleOp = interpolate(frame, [0, 15], [0, 1], { extrapolateRight: 'clamp' });
  const bubbles = [
    { side: 'r', text: 'qué tal va el drop', t: 20 },
    {
      side: 'l',
      text: '📊 Drop a 69/100 · Atención.\n💰 €7.775 en riesgo · €6.906 recuperables.\n🛡️ 2 VIPs por proteger.',
      t: 60,
    },
    { side: 'r', text: 'ejecuta la 1', t: 130 },
    { side: 'l', text: '✅ HECHO · Pausada la campaña Tiktok.\nAcabas de salvar €1.684.', t: 180 },
  ];
  const tagOp = interpolate(frame, [240, 270], [0, 1], { extrapolateRight: 'clamp' });

  return (
    <AbsoluteFill style={{ ...baseStyle, padding: 80, alignItems: 'center', justifyContent: 'center' }}>
      <div style={{ opacity: titleOp, fontSize: 40, fontWeight: 800, marginBottom: 30, color: C.green, letterSpacing: 4 }}>
        TELEGRAM · ACTUAR
      </div>
      <div style={{
        width: 900,
        background: '#EAF6F0',
        borderRadius: 24,
        padding: 40,
        display: 'flex',
        flexDirection: 'column',
        gap: 22,
        boxShadow: '0 20px 60px rgba(0,0,0,0.08)',
        minHeight: 700,
      }}>
        {bubbles.map((b, i) => {
          const op = interpolate(frame, [b.t, b.t + 12], [0, 1], { extrapolateRight: 'clamp', extrapolateLeft: 'clamp' });
          const slide = interpolate(frame, [b.t, b.t + 12], [15, 0], { extrapolateRight: 'clamp', extrapolateLeft: 'clamp' });
          const isUser = b.side === 'r';
          return (
            <div key={i} style={{
              alignSelf: isUser ? 'flex-end' : 'flex-start',
              display: 'flex',
              alignItems: 'flex-end',
              gap: 12,
              opacity: op,
              transform: `translateY(${slide}px)`,
              maxWidth: '78%',
            }}>
              {!isUser && (
                <div style={{
                  width: 48, height: 48, borderRadius: 24, background: '#FFFFFF',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  border: `2px solid ${C.green}`,
                  flexShrink: 0,
                }}>
                  <Img src={staticFile('scuffers_logo.png')} style={{ width: 32, height: 'auto' }} />
                </div>
              )}
              <div style={{
                background: isUser ? C.green : '#FFFFFF',
                color: isUser ? '#FFFFFF' : C.text,
                padding: '18px 24px',
                borderRadius: 18,
                fontSize: 28,
                fontWeight: 500,
                whiteSpace: 'pre-line',
                lineHeight: 1.4,
                boxShadow: '0 2px 8px rgba(0,0,0,0.05)',
              }}>
                {b.text}
              </div>
            </div>
          );
        })}
      </div>
      <div style={{ opacity: tagOp, marginTop: 30, fontSize: 24, color: C.gray, letterSpacing: 6 }}>
        IA CONVERSACIONAL · BILINGÜE
      </div>
    </AbsoluteFill>
  );
};

// =================== Scene 7: Discord ===================
const Scene7: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const titleOp = interpolate(frame, [0, 15], [0, 1], { extrapolateRight: 'clamp' });
  const cardOp = interpolate(frame, [10, 30], [0, 1], { extrapolateRight: 'clamp' });
  // counter: 0 -> 1 at frame 90, 1 -> 2 at frame 150
  let executed = 0;
  if (frame >= 90) executed = 1;
  if (frame >= 150) executed = 2;
  const tagOp = interpolate(frame, [200, 230], [0, 1], { extrapolateRight: 'clamp' });
  return (
    <AbsoluteFill style={{ ...baseStyle, padding: 80, alignItems: 'center', justifyContent: 'center' }}>
      <div style={{ opacity: titleOp, fontSize: 40, fontWeight: 800, marginBottom: 30, color: C.green, letterSpacing: 4 }}>
        DISCORD · VER
      </div>
      <div style={{
        width: 1100,
        background: '#2B2D31',
        borderRadius: 12,
        padding: 28,
        opacity: cardOp,
        transform: `translateY(${(1 - cardOp) * 20}px)`,
        boxShadow: '0 20px 60px rgba(0,0,0,0.2)',
      }}>
        <div style={{
          borderLeft: `5px solid ${C.green}`,
          background: '#1E1F22',
          borderRadius: 6,
          padding: 30,
          color: '#FFFFFF',
        }}>
          <div style={{ fontSize: 36, fontWeight: 800, marginBottom: 24 }}>
            ⚡ Drop Co-Pilot · 69/100 · ATENCIÓN
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20, fontSize: 26 }}>
            <div><span style={{ color: '#B5BAC1' }}>💰 Risk</span><br/><strong>€7.775</strong></div>
            <div><span style={{ color: '#B5BAC1' }}>💵 Recoverable</span><br/><strong>€6.906</strong></div>
            <div><span style={{ color: '#B5BAC1' }}>🛡️ VIPs</span><br/><strong>2 protegidos</strong></div>
            <div><span style={{ color: '#B5BAC1' }}>📋 Ejecutadas</span><br/>
              <strong style={{ color: C.green, fontStyle: 'italic', fontSize: 36 }}>{executed}/10</strong>
            </div>
          </div>
        </div>
      </div>
      <div style={{ opacity: tagOp, marginTop: 30, fontSize: 24, color: C.gray, letterSpacing: 6 }}>
        PANEL PINNEADO · AUTO-UPDATE
      </div>
    </AbsoluteFill>
  );
};

// =================== Scene 8: Shipping API ===================
const Scene8: React.FC = () => {
  const frame = useCurrentFrame();
  const titleOp = interpolate(frame, [0, 15], [0, 1], { extrapolateRight: 'clamp' });
  const orders = [
    { id: 'ORD-10568', state: 'Retrasado · riesgo 88%', color: C.red },
    { id: 'ORD-10460', state: 'Incidencia · revisión manual', color: C.amber },
    { id: 'ORD-10425', state: 'Retrasado · aduanas', color: C.amber },
    { id: 'ORD-10515', state: 'En tránsito · OK', color: C.green },
  ];
  const statsOp = interpolate(frame, [120, 145], [0, 1], { extrapolateRight: 'clamp' });
  const tagOp = interpolate(frame, [160, 185], [0, 1], { extrapolateRight: 'clamp' });
  return (
    <AbsoluteFill style={{ ...baseStyle, padding: 100, justifyContent: 'center' }}>
      <div style={{
        opacity: titleOp,
        fontSize: 64,
        fontWeight: 900,
        letterSpacing: -2,
        marginBottom: 40,
      }}>
        API DE ENVÍOS · INTEGRADA EN VIVO
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24 }}>
        {orders.map((o, i) => {
          const t = 20 + i * 18;
          const op = interpolate(frame, [t, t + 15], [0, 1], { extrapolateRight: 'clamp', extrapolateLeft: 'clamp' });
          const slide = interpolate(frame, [t, t + 15], [20, 0], { extrapolateRight: 'clamp', extrapolateLeft: 'clamp' });
          return (
            <div key={i} style={{
              opacity: op,
              transform: `translateY(${slide}px)`,
              background: '#FFFFFF',
              border: `1px solid ${C.border}`,
              borderLeft: `6px solid ${o.color}`,
              borderRadius: 8,
              padding: '28px 32px',
              boxShadow: '0 4px 20px rgba(0,0,0,0.05)',
            }}>
              <div style={{ fontSize: 36, fontWeight: 800, marginBottom: 8, fontFamily: 'monospace' }}>{o.id}</div>
              <div style={{ fontSize: 26, color: o.color, fontWeight: 700 }}>{o.state}</div>
            </div>
          );
        })}
      </div>
      <div style={{
        opacity: statsOp,
        marginTop: 40,
        fontSize: 38,
        fontWeight: 700,
        fontStyle: 'italic',
      }}>
        50 pedidos consultados · 10 incidencias detectadas
      </div>
      <div style={{ opacity: tagOp, marginTop: 20, fontSize: 26, color: C.green, letterSpacing: 4, fontWeight: 700 }}>
        REACCIONÓ AL CAMBIO DEL RETO EN 30 SEGUNDOS
      </div>
    </AbsoluteFill>
  );
};

// =================== Scene 9: Mobile dashboard ===================
const Scene9: React.FC = () => {
  const frame = useCurrentFrame();
  const phoneOp = interpolate(frame, [0, 25], [0, 1], { extrapolateRight: 'clamp' });
  const phoneSlide = interpolate(frame, [0, 25], [40, 0], { extrapolateRight: 'clamp' });
  const items = [
    'Login con 5 roles',
    'Filtros instantáneos',
    'Top 10 dinámico',
    'KPIs en tiempo real',
    'Chat widget IA',
    'Auto-refresh',
  ];
  return (
    <AbsoluteFill style={{ ...baseStyle, padding: 100, flexDirection: 'row', alignItems: 'center', gap: 80 }}>
      {/* Phone mockup */}
      <div style={{
        opacity: phoneOp,
        transform: `translateY(${phoneSlide}px)`,
        width: 420,
        height: 860,
        background: '#111111',
        borderRadius: 50,
        padding: 16,
        boxShadow: '0 30px 80px rgba(0,0,0,0.25)',
      }}>
        <div style={{
          width: '100%', height: '100%', background: '#FFFFFF', borderRadius: 36,
          padding: 24, display: 'flex', flexDirection: 'column', gap: 18,
        }}>
          <div style={{ fontSize: 14, color: C.gray, letterSpacing: 4, fontWeight: 700 }}>SCUFFERS · DROP</div>
          <div style={{ fontSize: 18, fontWeight: 700 }}>Health Score</div>
          <div style={{
            background: '#FBF1E0', borderRadius: 14, padding: 24, textAlign: 'center',
          }}>
            <div style={{ fontSize: 96, fontWeight: 900, fontStyle: 'italic', color: C.amber, lineHeight: 1 }}>69</div>
            <div style={{ fontSize: 16, color: C.amber, fontWeight: 700, marginTop: 6, letterSpacing: 2 }}>/ 100 · ATENCIÓN</div>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
            <div style={{ background: '#F4F4F4', padding: 14, borderRadius: 10 }}>
              <div style={{ fontSize: 12, color: C.gray }}>RIESGO</div>
              <div style={{ fontSize: 22, fontWeight: 800, color: C.red }}>€7.775</div>
            </div>
            <div style={{ background: '#F4F4F4', padding: 14, borderRadius: 10 }}>
              <div style={{ fontSize: 12, color: C.gray }}>RECUPERABLE</div>
              <div style={{ fontSize: 22, fontWeight: 800, color: C.green }}>€6.906</div>
            </div>
          </div>
          <div style={{
            border: `1px solid ${C.border}`,
            borderLeft: `5px solid ${C.green}`,
            borderRadius: 8, padding: 16,
          }}>
            <div style={{ fontSize: 14, color: C.gray, fontWeight: 700 }}>#01</div>
            <div style={{ fontSize: 18, fontWeight: 800, marginTop: 4 }}>Pausar campaña Tiktok</div>
            <div style={{ fontSize: 14, color: C.gray, marginTop: 4 }}>€1.684 recuperables</div>
          </div>
          <div style={{
            background: C.green, color: '#FFFFFF', padding: 14, borderRadius: 10,
            textAlign: 'center', fontWeight: 800, fontSize: 16,
          }}>
            EJECUTAR
          </div>
        </div>
      </div>
      {/* Right side */}
      <div style={{ flex: 1 }}>
        <div style={{
          fontSize: 56, fontWeight: 900, letterSpacing: -2, marginBottom: 30,
        }}>
          Cero código visible · 100% en castellano · móvil first
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          {items.map((it, i) => {
            const t = 30 + i * 12;
            const op = interpolate(frame, [t, t + 15], [0, 1], { extrapolateRight: 'clamp', extrapolateLeft: 'clamp' });
            const slide = interpolate(frame, [t, t + 15], [-20, 0], { extrapolateRight: 'clamp', extrapolateLeft: 'clamp' });
            return (
              <div key={i} style={{
                opacity: op,
                transform: `translateX(${slide}px)`,
                fontSize: 32,
                fontWeight: 700,
                paddingLeft: 22,
                borderLeft: `5px solid ${C.green}`,
              }}>
                {it}
              </div>
            );
          })}
        </div>
      </div>
    </AbsoluteFill>
  );
};

// =================== Scene 10: Cierre ===================
const Scene10: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const phraseOp = interpolate(frame, [0, 25], [0, 1], { extrapolateRight: 'clamp' });
  const logoOp = spring({ frame: frame - 25, fps, config: { damping: 200 } });
  const lines = [
    'Construido en 95 minutos con Claude Code',
    'github.com/aaangelmartin/scuffers-drop-copilot',
    'Ángel Martín Domínguez · #SCF-2026-1498',
  ];
  return (
    <AbsoluteFill style={{ ...baseStyle, justifyContent: 'center', alignItems: 'center', padding: 100 }}>
      <div style={{
        opacity: phraseOp,
        transform: `translateY(${(1 - phraseOp) * 20}px)`,
        fontSize: 84,
        fontWeight: 900,
        fontStyle: 'italic',
        letterSpacing: -3,
        textAlign: 'center',
        color: C.green,
        lineHeight: 1.1,
        maxWidth: 1500,
      }}>
        PROTECTING THE DROP, ONE DECISION AT A TIME.
      </div>
      <div style={{ opacity: logoOp, marginTop: 50 }}>
        <Img src={staticFile('scuffers_logo.png')} style={{ width: 200, height: 'auto' }} />
      </div>
      <div style={{ marginTop: 40, display: 'flex', flexDirection: 'column', gap: 8, alignItems: 'center' }}>
        {lines.map((l, i) => {
          const t = 50 + i * 12;
          const op = interpolate(frame, [t, t + 15], [0, 1], { extrapolateRight: 'clamp', extrapolateLeft: 'clamp' });
          return (
            <div key={i} style={{ opacity: op, fontSize: 22, color: C.gray, fontWeight: 600 }}>{l}</div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

// =================== Crossfade wrapper ===================
const SceneWrap: React.FC<{ dur: number; children: React.ReactNode }> = ({ dur, children }) => {
  // Inside a Sequence, useCurrentFrame is already local (0..dur-1)
  const local = useCurrentFrame();
  const inOp = interpolate(local, [0, 6], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  const outOp = interpolate(local, [dur - 6, dur], [1, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  const op = Math.min(inOp, outOp);
  return <AbsoluteFill style={{ opacity: op }}>{children}</AbsoluteFill>;
};

export const ScuffersVideo: React.FC = () => {
  const scenes: Array<[string, number, React.FC]> = [
    ['s1', S.s1, Scene1],
    ['s2', S.s2, Scene2],
    ['s3', S.s3, Scene3],
    ['s4', S.s4, Scene4],
    ['s5', S.s5, Scene5],
    ['s6', S.s6, Scene6],
    ['s7', S.s7, Scene7],
    ['s8', S.s8, Scene8],
    ['s9', S.s9, Scene9],
    ['s10', S.s10, Scene10],
  ];
  let cursor = 0;
  return (
    <AbsoluteFill style={baseStyle}>
      {scenes.map(([key, sec, Comp]) => {
        const start = cursor;
        const dur = f(sec);
        cursor += dur;
        return (
          <Sequence key={key} from={start} durationInFrames={dur}>
            <SceneWrap dur={dur}>
              <Comp />
            </SceneWrap>
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};
