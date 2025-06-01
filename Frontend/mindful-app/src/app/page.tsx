import Link from 'next/link';
import { FiArrowRight, FiHeart, FiMessageCircle, FiSun } from 'react-icons/fi';

export default function Home() {
  return (
    <div style={{ minHeight: '100vh' }}>
      {/* Header */}
      <header style={{ padding: '1.5rem 1rem' }}>
        <div style={{ 
          maxWidth: '80rem', 
          margin: '0 auto', 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center' 
        }}>
          <div style={{ display: 'flex', alignItems: 'center' }}>
            <div style={{ 
              width: '2.5rem', 
              height: '2.5rem', 
              backgroundColor: 'var(--color-sage-500)', 
              borderRadius: '9999px', 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'center',
              boxShadow: '0 4px 8px -2px rgba(128, 143, 118, 0.2)'
            }}>
              <span style={{ color: 'white', fontWeight: 600, fontSize: '1.125rem' }}>M</span>
            </div>
            <h1 style={{ marginLeft: '0.75rem', fontSize: '1.25rem', fontWeight: 600, color: 'var(--color-sage-800)' }}>Ami</h1>
          </div>
          
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <Link 
              href="/login" 
              style={{ 
                padding: '0.5rem 1rem', 
                color: 'var(--color-sage-700)', 
                fontWeight: 500,
                transition: 'all 300ms ease'
              }}
            >
              Sign in
            </Link>
            <Link 
              href="/register" 
              className="btn btn-primary floating-delayed"
            >
              Get started
            </Link>
          </div>
        </div>
      </header>
      
      {/* Hero section */}
      <section style={{ padding: '4rem 1rem' }}>
        <div style={{ maxWidth: '64rem', margin: '0 auto', textAlign: 'center' }}>
          <h1 className="floating" style={{ 
            fontSize: 'clamp(2rem, 5vw, 3.75rem)', 
            fontWeight: 700, 
            color: 'var(--color-sage-800)', 
            lineHeight: 1.2,
            maxWidth: '90%',
            margin: '0 auto'
          }}>
            Find calm in the chaos with your AI mental health coach
          </h1>
          <p className="floating-delayed" style={{ 
            marginTop: '1.5rem', 
            fontSize: '1.25rem', 
            color: 'var(--color-sage-700)', 
            maxWidth: '48rem', 
            margin: '1.5rem auto 0',
            lineHeight: 1.6
          }}>
            A gentle, supportive AI companion to help you navigate life's challenges, develop mindfulness,
            and build lasting mental wellbeing.
          </p>
          <div style={{ marginTop: '2.5rem' }} className="floating">
            <Link 
              href="/register" 
              className="btn btn-primary"
              style={{
                padding: '0.75rem 2rem',
                fontSize: '1.125rem',
                display: 'inline-flex',
                alignItems: 'center'
              }}
            >
              Begin your journey
              <FiArrowRight style={{ marginLeft: '0.5rem' }} />
            </Link>
          </div>
          
          <div className="card" style={{ 
            marginTop: '4rem',
            maxWidth: '90%',
            margin: '4rem auto 0',
            background: 'rgba(255, 253, 247, 0.5)',
          }}>
            <div style={{ 
              display: 'grid', 
              gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', 
              gap: '1.5rem' 
            }}>
              <div className="floating" style={{ 
                padding: '1.5rem', 
                borderRadius: '1.2rem', 
                background: 'linear-gradient(to bottom right, var(--color-cream-50), var(--color-cream-100))', 
                border: '1px solid var(--color-cream-200)',
                boxShadow: '0 8px 16px -4px rgba(158, 138, 99, 0.08)',
                transition: 'all 400ms ease'
              }}>
                <div style={{ 
                  width: '3.5rem', 
                  height: '3.5rem', 
                  borderRadius: '9999px', 
                  background: 'rgba(128, 143, 118, 0.1)', 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'center', 
                  margin: '0 auto',
                  boxShadow: '0 6px 12px -4px rgba(128, 143, 118, 0.15)'
                }}>
                  <FiHeart style={{ color: 'var(--color-sage-600)', fontSize: '1.4rem' }} />
                </div>
                <h3 style={{ marginTop: '1.2rem', fontSize: '1.25rem', fontWeight: 600, color: 'var(--color-sage-800)' }}>Emotional Support</h3>
                <p style={{ marginTop: '0.8rem', color: 'var(--color-sage-700)', lineHeight: 1.6 }}>A compassionate space to process emotions and develop healthy coping strategies</p>
              </div>
              
              <div className="floating-delayed" style={{ 
                padding: '1.5rem', 
                borderRadius: '1.2rem', 
                background: 'linear-gradient(to bottom right, var(--color-cream-50), var(--color-cream-100))', 
                border: '1px solid var(--color-cream-200)',
                boxShadow: '0 8px 16px -4px rgba(158, 138, 99, 0.08)',
                transition: 'all 400ms ease'
              }}>
                <div style={{ 
                  width: '3.5rem', 
                  height: '3.5rem', 
                  borderRadius: '9999px', 
                  background: 'rgba(126, 147, 159, 0.1)', 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'center', 
                  margin: '0 auto',
                  boxShadow: '0 6px 12px -4px rgba(126, 147, 159, 0.15)'
                }}>
                  <FiMessageCircle style={{ color: 'var(--color-mist-600)', fontSize: '1.4rem' }} />
                </div>
                <h3 style={{ marginTop: '1.2rem', fontSize: '1.25rem', fontWeight: 600, color: 'var(--color-sage-800)' }}>Guided Conversations</h3>
                <p style={{ marginTop: '0.8rem', color: 'var(--color-sage-700)', lineHeight: 1.6 }}>Therapeutic discussions that provide insight, clarity, and personal growth</p>
              </div>
              
              <div className="floating" style={{ 
                padding: '1.5rem', 
                borderRadius: '1.2rem', 
                background: 'linear-gradient(to bottom right, var(--color-cream-50), var(--color-cream-100))', 
                border: '1px solid var(--color-cream-200)',
                boxShadow: '0 8px 16px -4px rgba(158, 138, 99, 0.08)',
                transition: 'all 400ms ease'
              }}>
                <div style={{ 
                  width: '3.5rem', 
                  height: '3.5rem', 
                  borderRadius: '9999px',
                  background: 'rgba(206, 186, 145, 0.15)', 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'center', 
                  margin: '0 auto',
                  boxShadow: '0 6px 12px -4px rgba(206, 186, 145, 0.2)'
                }}>
                  <FiSun style={{ color: 'var(--color-cream-700)', fontSize: '1.4rem' }} />
                </div>
                <h3 style={{ marginTop: '1.2rem', fontSize: '1.25rem', fontWeight: 600, color: 'var(--color-sage-800)' }}>Mindfulness Practice</h3>
                <p style={{ marginTop: '0.8rem', color: 'var(--color-sage-700)', lineHeight: 1.6 }}>Learn to stay present, reduce stress, and cultivate inner peace</p>
              </div>
            </div>
          </div>
        </div>
      </section>
      
      {/* Footer */}
      <footer style={{ 
        padding: '3rem 1rem', 
        borderTop: '1px solid var(--color-cream-200)',
        marginTop: '2rem'
      }}>
        <div style={{ maxWidth: '80rem', margin: '0 auto', textAlign: 'center' }}>
          <p style={{ color: 'var(--color-sage-600)' }}>&copy; {new Date().getFullYear()} Mindful AI Coach. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}
