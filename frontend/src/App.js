import React, { useEffect, useState } from 'react';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5050';

const COLORS = {
  brown: '#6F4E37',
  cream: '#F5E9DA',
  white: '#FFFFFF',
  black: '#222222',
  gold: '#FFD700',
  green: '#4BB543',
  red: '#D7263D',
};

// Toast-компонент
function Toast({ open, message, type = 'success', onClose }) {
  if (!open) return null;
  return (
    <div style={{
      position: 'fixed', top: 32, right: 32, zIndex: 2000,
      background: type === 'success' ? COLORS.green : COLORS.red,
      color: COLORS.white, padding: '16px 32px', borderRadius: 10,
      fontWeight: 600, fontSize: 17, boxShadow: '0 2px 16px #0003',
      minWidth: 220, textAlign: 'center',
      animation: 'fadein 0.3s',
    }}>
      {message}
      <button onClick={onClose} style={{ marginLeft: 18, background: 'none', border: 'none', color: COLORS.white, fontSize: 20, cursor: 'pointer' }}>&times;</button>
    </div>
  );
}

function StarRating({ value, onChange, readOnly = false }) {
  return (
    <div style={{ display: 'flex', gap: 2 }}>
      {[1, 2, 3, 4, 5].map((star) => (
        <span
          key={star}
          style={{
            color: star <= value ? COLORS.gold : COLORS.brown,
            fontSize: 20,
            cursor: readOnly ? 'default' : 'pointer',
            userSelect: 'none',
          }}
          onClick={() => !readOnly && onChange(star)}
        >
          ★
        </span>
      ))}
    </div>
  );
}

// App.js — основной компонент приложения обмена книгами в ЦУ
// В этом файле реализованы все основные страницы, роутинг, бизнес-логика, взаимодействие с backend API

/**
 * Основной компонент приложения.
 * Управляет состоянием пользователя, книг, обменов, отзывов, отображением страниц и обработкой событий.
 * @returns {JSX.Element}
 */
function App() {
  // Авторизация
  const [user, setUser] = useState(() => {
    try {
      const u = localStorage.getItem('user');
      return u ? JSON.parse(u) : null;
    } catch { return null; }
  });
  const [authMode, setAuthMode] = useState('welcome'); // welcome | login | register
  const [authForm, setAuthForm] = useState({ username: '', email: '' });
  const [authError, setAuthError] = useState('');
  const [authLoading, setAuthLoading] = useState(false);
  const [showRegisterBtn, setShowRegisterBtn] = useState(false);

  // Toast state
  const [toast, setToast] = useState({ open: false, message: '', type: 'success' });
  const showToast = (message, type = 'success') => setToast({ open: true, message, type });
  const closeToast = () => setToast({ ...toast, open: false });

  const [books, setBooks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [form, setForm] = useState({ title: '', author: '', description: '' });
  const [formError, setFormError] = useState('');
  const [adding, setAdding] = useState(false);
  // Фильтры
  const [filters, setFilters] = useState({ title: '', author: '', is_available: '' });
  const [filtering, setFiltering] = useState(false);
  // Отзывы
  const [showReviews, setShowReviews] = useState(null); // bookId | null
  const [reviews, setReviews] = useState([]);
  const [reviewsLoading, setReviewsLoading] = useState(false);
  const [reviewForm, setReviewForm] = useState({ rating: 5, text: '' });
  const [reviewError, setReviewError] = useState('');
  const [reviewAdding, setReviewAdding] = useState(false);
  // Для обмена
  const [showExchange, setShowExchange] = useState(null); // bookId | null
  const [myBooks, setMyBooks] = useState([]); // книги пользователя (owner_id=1)
  const [exchangeBookId, setExchangeBookId] = useState('');
  const [exchangeError, setExchangeError] = useState('');
  const [exchangeLoading, setExchangeLoading] = useState(false);
  // Управление заявками
  const [showMyExchanges, setShowMyExchanges] = useState(false);
  const [showIncomingExchanges, setShowIncomingExchanges] = useState(false);
  const [myExchanges, setMyExchanges] = useState([]);
  const [incomingExchanges, setIncomingExchanges] = useState([]);
  const [exchangesLoading, setExchangesLoading] = useState(false);
  const [exchangeActionLoading, setExchangeActionLoading] = useState(false);

  // Профиль
  const [showProfile, setShowProfile] = useState(false);
  const [profileTab, setProfileTab] = useState('books');
  const [profileBooks, setProfileBooks] = useState([]);
  const [profileReviews, setProfileReviews] = useState([]);
  const [profileExchanges, setProfileExchanges] = useState([]);
  const [profileLoading, setProfileLoading] = useState(false);

  // Админ-панель
  const isAdmin = user && user.email === 'admin@edu.centraluniversity.ru';
  const [showAdmin, setShowAdmin] = useState(false);
  const [adminStats, setAdminStats] = useState({ users: 0, books: 0, exchanges: 0 });
  const [adminUsers, setAdminUsers] = useState([]);
  const [adminBooks, setAdminBooks] = useState([]);
  const [adminExchanges, setAdminExchanges] = useState([]);
  const [adminLoading, setAdminLoading] = useState(false);

  const PLACES = [
    'Профессорский клуб 4 этаж',
    'Профессорский клуб 8 этаж',
    'Спортивный зал 1 этаж',
    'Общий холл 1 этаж',
    'Аудитория B816',
    'Аудитория B422',
    'Аудитория B104',
    'Аудитория "Эльбрус"',
    'Уголок Сибура 5 этаж',
  ];
  const [exchangePlace, setExchangePlace] = useState(PLACES[0]);

  const fetchBooks = () => {
    setLoading(true);
    setError(null);
    let url = `${API_URL}/books`;
    const params = [];
    if (filters.title) params.push(`title=${encodeURIComponent(filters.title)}`);
    if (filters.author) params.push(`author=${encodeURIComponent(filters.author)}`);
    if (filters.is_available) params.push(`is_available=${filters.is_available}`);
    if (params.length) url += '?' + params.join('&');
    fetch(url)
      .then((res) => {
        if (!res.ok) throw new Error('Ошибка загрузки данных');
        return res.json();
      })
      .then((data) => {
        setBooks(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchBooks();
    // eslint-disable-next-line
  }, []);

  const handleInput = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
    setFormError('');
  };

  const handleAddBook = async (e) => {
    e.preventDefault();
    if (!form.title.trim() || !form.author.trim()) {
      setFormError('Заполните название и автора');
      return;
    }
    setAdding(true);
    setFormError('');
    try {
      const res = await fetch(`${API_URL}/books`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...form, owner_id: user.id })
      });
      if (!res.ok) throw new Error('Ошибка при добавлении книги');
      const newBook = await res.json();
      setBooks([ ...books, newBook ]);
      setForm({ title: '', author: '', description: '' });
    } catch (err) {
      setFormError('Ошибка при добавлении книги');
    } finally {
      setAdding(false);
    }
  };

  // Фильтрация
  const handleFilterChange = (e) => {
    setFilters({ ...filters, [e.target.name]: e.target.value });
  };
  const handleFilterSubmit = (e) => {
    e.preventDefault();
    setFiltering(true);
    fetchBooks();
    setFiltering(false);
  };
  const handleFilterReset = () => {
    setFilters({ title: '', author: '', is_available: '' });
    setFiltering(true);
    setTimeout(() => {
      fetchBooks();
      setFiltering(false);
    }, 0);
  };

  // Отзывы
  const openReviews = (bookId) => {
    setShowReviews(bookId);
    setReviewsLoading(true);
    setReviewForm({ rating: 5, text: '' });
    setReviewError('');
    fetch(`${API_URL}/reviews?book_id=${bookId}`)
      .then((res) => res.json())
      .then((data) => {
        setReviews(data);
        setReviewsLoading(false);
      })
      .catch(() => {
        setReviews([]);
        setReviewsLoading(false);
      });
  };
  const closeReviews = () => {
    setShowReviews(null);
    setReviews([]);
    setReviewForm({ rating: 5, text: '' });
    setReviewError('');
  };
  const handleReviewInput = (e) => {
    setReviewForm({ ...reviewForm, [e.target.name]: e.target.value });
    setReviewError('');
  };
  const handleReviewRating = (val) => {
    setReviewForm({ ...reviewForm, rating: val });
  };
  const handleAddReview = async (e) => {
    e.preventDefault();
    if (!reviewForm.text.trim()) {
      setReviewError('Введите текст отзыва');
      return;
    }
    setReviewAdding(true);
    setReviewError('');
    try {
      const res = await fetch(`${API_URL}/reviews`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          book_id: showReviews,
          user_id: user.id,
          text: reviewForm.text,
          rating: reviewForm.rating
        })
      });
      if (!res.ok) throw new Error('Ошибка при добавлении отзыва');
      const newReview = await res.json();
      setReviews([ ...reviews, newReview ]);
      setReviewForm({ rating: 5, text: '' });
    } catch (err) {
      setReviewError('Ошибка при добавлении отзыва');
    } finally {
      setReviewAdding(false);
    }
  };

  // Получить свои книги (owner_id=1)
  const fetchMyBooks = () => {
    fetch(`${API_URL}/books?owner_id=${user.id}`)
      .then((res) => res.json())
      .then((data) => setMyBooks(data))
      .catch(() => setMyBooks([]));
  };

  // Открыть модалку обмена
  const openExchange = (bookId) => {
    setShowExchange(bookId);
    setExchangeBookId('');
    setExchangeError('');
    fetchMyBooks();
  };
  const closeExchange = () => {
    setShowExchange(null);
    setExchangeBookId('');
    setExchangeError('');
  };
  // Отправить заявку на обмен
  const handleExchange = async (e) => {
    e.preventDefault();
    if (!exchangeBookId) {
      setExchangeError('Выберите свою книгу для обмена');
      return;
    }
    setExchangeLoading(true);
    setExchangeError('');
    try {
      const res = await fetch(`${API_URL}/exchanges`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: user.id,
          book_id: showExchange,
          place: exchangePlace
        })
      });
      if (!res.ok) throw new Error('Ошибка при создании заявки');
      closeExchange();
      showToast('Заявка на обмен отправлена!', 'success');
      fetchMyExchanges();
    } catch (err) {
      setExchangeError('Ошибка при создании заявки');
      showToast('Ошибка при создании заявки', 'error');
    } finally {
      setExchangeLoading(false);
    }
  };

  // Получить отправленные заявки (user_id=1)
  const fetchMyExchanges = () => {
    setExchangesLoading(true);
    fetch(`${API_URL}/exchanges?user_id=${user.id}`)
      .then((res) => res.json())
      .then((data) => { setMyExchanges(data); setExchangesLoading(false); })
      .catch(() => { setMyExchanges([]); setExchangesLoading(false); });
  };
  // Получить входящие заявки (на мои книги)
  const fetchIncomingExchanges = () => {
    setExchangesLoading(true);
    fetch(`${API_URL}/exchanges?owner_id=${user.id}`)
      .then((res) => res.json())
      .then((data) => { setIncomingExchanges(data); setExchangesLoading(false); })
      .catch(() => { setIncomingExchanges([]); setExchangesLoading(false); });
  };

  // Принять/отклонить заявку
  const handleExchangeAction = async (exchangeId, action) => {
    setExchangeActionLoading(true);
    try {
      const res = await fetch(`${API_URL}/exchanges/${exchangeId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action })
      });
      if (!res.ok) throw new Error('Ошибка');
      showToast(action === 'accept' ? 'Обмен подтверждён!' : 'Заявка отклонена', 'success');
      fetchIncomingExchanges();
      fetchBooks();
    } catch {
      showToast('Ошибка при обработке заявки', 'error');
    } finally {
      setExchangeActionLoading(false);
    }
  };

  // Авторизация/регистрация
  const handleAuthInput = (e) => {
    setAuthForm({ ...authForm, [e.target.name]: e.target.value });
    setAuthError('');
    setShowRegisterBtn(false);
  };
  const handleLogin = async (e) => {
    e.preventDefault();
    setAuthError('');
    setShowRegisterBtn(false);
    setAuthLoading(true);
    try {
      const res = await fetch(`${API_URL}/users?email=${encodeURIComponent(authForm.email)}`);
      const users = await res.json();
      const currentUser = users.find(u => u.username === authForm.username);
      if (!currentUser) {
        setAuthError('Этот пользователь не зарегистрирован');
        setShowRegisterBtn(true);
        setAuthLoading(false);
        return;
      }
      setUser(currentUser);
      localStorage.setItem('user', JSON.stringify(currentUser));
      showToast('Вход выполнен!', 'success');
      setAuthMode('');
    } catch {
      setAuthError('Ошибка входа');
      showToast('Ошибка входа', 'error');
    } finally {
      setAuthLoading(false);
    }
  };
  const handleRegister = async (e) => {
    e.preventDefault();
    setAuthError('');
    setAuthLoading(true);
    try {
      // Проверка на существование email
      const res = await fetch(`${API_URL}/users?email=${encodeURIComponent(authForm.email)}`);
      const users = await res.json();
      if (users.length > 0) {
        setAuthError('Пользователь с такой почтой уже зарегистрирован');
        setAuthLoading(false);
        return;
      }
      // Регистрируем
      const regRes = await fetch(`${API_URL}/users`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(authForm)
      });
      if (!regRes.ok) throw new Error('Ошибка регистрации');
      const newUser = await regRes.json();
      setUser(newUser);
      localStorage.setItem('user', JSON.stringify(newUser));
      showToast('Регистрация успешна!', 'success');
      setAuthMode('');
    } catch {
      setAuthError('Ошибка регистрации');
      showToast('Ошибка регистрации', 'error');
    } finally {
      setAuthLoading(false);
    }
  };
  const handleLogout = () => {
    setUser(null);
    localStorage.removeItem('user');
    setAuthMode('welcome');
    setAuthForm({ username: '', email: '' });
    setAuthError('');
    setShowRegisterBtn(false);
  };

  // Получить данные профиля
  const fetchProfileData = () => {
    setProfileLoading(true);
    Promise.all([
      fetch(`${API_URL}/books?owner_id=${user.id}`).then(res => res.json()),
      fetch(`${API_URL}/reviews?user_id=${user.id}`).then(res => res.json()),
      fetch(`${API_URL}/exchanges?user_id=${user.id}&status=accepted`).then(res => res.json())
    ]).then(([books, reviews, exchanges]) => {
      setProfileBooks(books);
      setProfileReviews(reviews);
      setProfileExchanges(exchanges);
      setProfileLoading(false);
    }).catch(() => {
      setProfileBooks([]); setProfileReviews([]); setProfileExchanges([]); setProfileLoading(false);
    });
  };

  // Админ-панель
  const fetchAdminData = () => {
    setAdminLoading(true);
    Promise.all([
      fetch(`${API_URL}/users`).then(res => res.json()),
      fetch(`${API_URL}/books`).then(res => res.json()),
      fetch(`${API_URL}/exchanges`).then(res => res.json())
    ]).then(([users, books, exchanges]) => {
      const acceptedExchanges = exchanges.filter(ex => ex.status === 'accepted');
      setAdminStats({ users: users.length, books: books.length, exchanges: acceptedExchanges.length });
      setAdminUsers(users);
      setAdminBooks(books);
      setAdminExchanges(acceptedExchanges);
      setAdminLoading(false);
    }).catch(() => {
      setAdminStats({ users: 0, books: 0, exchanges: 0 });
      setAdminUsers([]); setAdminBooks([]); setAdminExchanges([]); setAdminLoading(false);
    });
  };

  // Главная страница (до входа)
  if (!user && authMode === 'welcome') {
    return (
      <div style={{ minHeight: '100vh', background: COLORS.cream, display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column' }}>
        <Toast open={toast.open} message={toast.message} type={toast.type} onClose={closeToast} />
        <div style={{ background: COLORS.white, borderRadius: 16, boxShadow: '0 2px 16px #0001', padding: 40, minWidth: 340, maxWidth: 500, marginBottom: 32 }}>
          <h2 style={{ color: COLORS.brown, margin: 0, fontWeight: 700, fontSize: 26, textAlign: 'center' }}>Сервис обмена книгами в ЦУ</h2>
          <div style={{ color: COLORS.black, fontSize: 17, margin: '18px 0 0 0', textAlign: 'center' }}>
            Платформа для обмена книгами между студентами и сотрудниками <b>Центрального университета</b> с возможностью оставлять отзывы, искать книги по фильтрам и вести историю обменов. <br />
            <span style={{ color: COLORS.brown, fontSize: 15 }}>Войдите или зарегистрируйтесь, чтобы начать пользоваться сервисом.</span>
          </div>
        </div>
        <div style={{ display: 'flex', gap: 18 }}>
          <button onClick={() => setAuthMode('login')} style={{ background: COLORS.brown, color: COLORS.white, border: 'none', borderRadius: 6, padding: '14px 32px', fontWeight: 600, fontSize: 17, cursor: 'pointer' }}>Войти</button>
          <button onClick={() => setAuthMode('register')} style={{ background: COLORS.white, color: COLORS.brown, border: `2px solid ${COLORS.brown}`, borderRadius: 6, padding: '14px 32px', fontWeight: 600, fontSize: 17, cursor: 'pointer' }}>Зарегистрироваться</button>
        </div>
      </div>
    );
  }

  // Форма входа
  if (!user && authMode === 'login') {
    return (
      <div style={{ minHeight: '100vh', background: COLORS.cream, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <Toast open={toast.open} message={toast.message} type={toast.type} onClose={closeToast} />
        <form onSubmit={handleLogin} style={{ background: COLORS.white, borderRadius: 16, boxShadow: '0 2px 16px #0001', padding: 40, minWidth: 320, display: 'flex', flexDirection: 'column', gap: 18 }}>
          <h2 style={{ color: COLORS.brown, margin: 0, fontWeight: 700, fontSize: 26, textAlign: 'center' }}>Вход</h2>
          <input
            name="username"
            placeholder="Имя пользователя"
            value={authForm.username}
            onChange={handleAuthInput}
            style={{ padding: 12, borderRadius: 6, border: `1px solid ${COLORS.brown}`, fontSize: 16 }}
            required
          />
          <input
            name="email"
            placeholder="Email"
            value={authForm.email}
            onChange={handleAuthInput}
            style={{ padding: 12, borderRadius: 6, border: `1px solid ${COLORS.brown}`, fontSize: 16 }}
            required
          />
          {authError && <div style={{ color: COLORS.red, fontSize: 15 }}>{authError}</div>}
          <button
            type="submit"
            disabled={authLoading}
            style={{ background: COLORS.brown, color: COLORS.white, border: 'none', borderRadius: 6, padding: '12px 0', fontWeight: 600, fontSize: 16, cursor: authLoading ? 'not-allowed' : 'pointer', opacity: authLoading ? 0.7 : 1 }}
          >
            {authLoading ? 'Вход...' : 'Войти'}
          </button>
          {showRegisterBtn && (
            <button type="button" onClick={() => setAuthMode('register')} style={{ background: COLORS.white, color: COLORS.brown, border: `1px solid ${COLORS.brown}`, borderRadius: 6, padding: '10px 0', fontWeight: 600, fontSize: 15, marginTop: 8, cursor: 'pointer' }}>Зарегистрироваться</button>
          )}
          <button type="button" onClick={() => setAuthMode('welcome')} style={{ background: 'none', color: COLORS.brown, border: 'none', fontSize: 15, marginTop: 8, cursor: 'pointer' }}>Назад</button>
        </form>
      </div>
    );
  }

  // Форма регистрации
  if (!user && authMode === 'register') {
    return (
      <div style={{ minHeight: '100vh', background: COLORS.cream, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <Toast open={toast.open} message={toast.message} type={toast.type} onClose={closeToast} />
        <form onSubmit={handleRegister} style={{ background: COLORS.white, borderRadius: 16, boxShadow: '0 2px 16px #0001', padding: 40, minWidth: 320, display: 'flex', flexDirection: 'column', gap: 18 }}>
          <h2 style={{ color: COLORS.brown, margin: 0, fontWeight: 700, fontSize: 26, textAlign: 'center' }}>Регистрация</h2>
          <input
            name="username"
            placeholder="Имя пользователя"
            value={authForm.username}
            onChange={handleAuthInput}
            style={{ padding: 12, borderRadius: 6, border: `1px solid ${COLORS.brown}`, fontSize: 16 }}
            required
          />
          <input
            name="email"
            placeholder="Email"
            value={authForm.email}
            onChange={handleAuthInput}
            style={{ padding: 12, borderRadius: 6, border: `1px solid ${COLORS.brown}`, fontSize: 16 }}
            required
          />
          {authError && <div style={{ color: COLORS.red, fontSize: 15 }}>{authError}</div>}
          <button
            type="submit"
            disabled={authLoading}
            style={{ background: COLORS.brown, color: COLORS.white, border: 'none', borderRadius: 6, padding: '12px 0', fontWeight: 600, fontSize: 16, cursor: authLoading ? 'not-allowed' : 'pointer', opacity: authLoading ? 0.7 : 1 }}
          >
            {authLoading ? 'Регистрация...' : 'Зарегистрироваться'}
          </button>
          <button type="button" onClick={() => setAuthMode('welcome')} style={{ background: 'none', color: COLORS.brown, border: 'none', fontSize: 15, marginTop: 8, cursor: 'pointer' }}>Назад</button>
        </form>
      </div>
    );
  }

  return (
    <div style={{ minHeight: '100vh', background: COLORS.cream, fontFamily: 'Inter, Arial, sans-serif' }}>
      <Toast open={toast.open} message={toast.message} type={toast.type} onClose={closeToast} />
      <header style={{ background: COLORS.brown, color: COLORS.white, padding: '24px 0', textAlign: 'center', letterSpacing: 1, position: 'relative' }}>
        <h1 style={{ margin: 0, fontWeight: 700, fontSize: 32 }}>Обмен книгами в ЦУ</h1>
        <div style={{ position: 'absolute', right: 32, top: 24, display: 'flex', gap: 12 }}>
          {isAdmin && <button onClick={() => { setShowAdmin(true); fetchAdminData(); }} style={{ background: COLORS.white, color: COLORS.brown, border: 'none', borderRadius: 6, padding: '8px 18px', fontWeight: 600, fontSize: 15, cursor: 'pointer', boxShadow: '0 1px 6px #0001' }}>Админ</button>}
          <button onClick={() => { setShowProfile(true); setProfileTab('books'); fetchProfileData(); }} style={{ background: COLORS.white, color: COLORS.brown, border: 'none', borderRadius: 6, padding: '8px 18px', fontWeight: 600, fontSize: 15, cursor: 'pointer', boxShadow: '0 1px 6px #0001' }}>Профиль</button>
          <button onClick={() => { setShowMyExchanges(true); fetchMyExchanges(); }} style={{ background: COLORS.white, color: COLORS.brown, border: 'none', borderRadius: 6, padding: '8px 18px', fontWeight: 600, fontSize: 15, cursor: 'pointer', boxShadow: '0 1px 6px #0001' }}>Мои заявки</button>
          <button onClick={() => { setShowIncomingExchanges(true); fetchIncomingExchanges(); }} style={{ background: COLORS.white, color: COLORS.brown, border: 'none', borderRadius: 6, padding: '8px 18px', fontWeight: 600, fontSize: 15, cursor: 'pointer', boxShadow: '0 1px 6px #0001' }}>Входящие заявки</button>
          <button onClick={handleLogout} style={{ background: COLORS.white, color: COLORS.brown, border: 'none', borderRadius: 6, padding: '8px 18px', fontWeight: 600, fontSize: 15, cursor: 'pointer', boxShadow: '0 1px 6px #0001' }}>Выйти</button>
        </div>
      </header>
      <main style={{ maxWidth: 700, margin: '40px auto', background: COLORS.white, borderRadius: 16, boxShadow: '0 2px 16px #0001', padding: 40 }}>
        {/* Форма добавления книги */}
        <section style={{ marginBottom: 36 }}>
          <form onSubmit={handleAddBook} style={{ display: 'flex', flexDirection: 'column', gap: 14, background: COLORS.cream, borderRadius: 10, padding: 24, boxShadow: '0 1px 6px #0001' }}>
            <div style={{ fontWeight: 600, fontSize: 18, color: COLORS.brown, marginBottom: 4 }}>Добавить книгу для обмена</div>
            <input
              name="title"
              placeholder="Название книги"
              value={form.title}
              onChange={handleInput}
              style={{ padding: 10, borderRadius: 6, border: `1px solid ${COLORS.brown}`, fontSize: 16 }}
              required
            />
            <input
              name="author"
              placeholder="Автор книги"
              value={form.author}
              onChange={handleInput}
              style={{ padding: 10, borderRadius: 6, border: `1px solid ${COLORS.brown}`, fontSize: 16 }}
              required
            />
            <textarea
              name="description"
              placeholder="Описание (необязательно)"
              value={form.description}
              onChange={handleInput}
              style={{ padding: 10, borderRadius: 6, border: `1px solid ${COLORS.brown}`, fontSize: 16, resize: 'vertical', minHeight: 60 }}
            />
            {formError && <div style={{ color: 'red', fontSize: 15 }}>{formError}</div>}
            <button
              type="submit"
              disabled={adding}
              style={{
                background: COLORS.brown,
                color: COLORS.white,
                border: 'none',
                borderRadius: 6,
                padding: '12px 0',
                fontWeight: 600,
                fontSize: 16,
                cursor: adding ? 'not-allowed' : 'pointer',
                opacity: adding ? 0.7 : 1,
                marginTop: 6,
              }}
            >
              {adding ? 'Добавление...' : 'Добавить книгу'}
            </button>
          </form>
        </section>
        {/* Фильтрация и поиск */}
        <section style={{ marginBottom: 28 }}>
          <form onSubmit={handleFilterSubmit} style={{ display: 'flex', gap: 12, alignItems: 'flex-end', flexWrap: 'wrap', background: COLORS.cream, borderRadius: 10, padding: 18, boxShadow: '0 1px 6px #0001' }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
              <label style={{ color: COLORS.brown, fontWeight: 500, fontSize: 15 }}>Название</label>
              <input
                name="title"
                value={filters.title}
                onChange={handleFilterChange}
                placeholder="Поиск по названию"
                style={{ padding: 8, borderRadius: 6, border: `1px solid ${COLORS.brown}`, fontSize: 15, minWidth: 120 }}
              />
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
              <label style={{ color: COLORS.brown, fontWeight: 500, fontSize: 15 }}>Автор</label>
              <input
                name="author"
                value={filters.author}
                onChange={handleFilterChange}
                placeholder="Поиск по автору"
                style={{ padding: 8, borderRadius: 6, border: `1px solid ${COLORS.brown}`, fontSize: 15, minWidth: 120 }}
              />
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
              <label style={{ color: COLORS.brown, fontWeight: 500, fontSize: 15 }}>Доступность</label>
              <select
                name="is_available"
                value={filters.is_available}
                onChange={handleFilterChange}
                style={{ padding: 8, borderRadius: 6, border: `1px solid ${COLORS.brown}`, fontSize: 15, minWidth: 120 }}
              >
                <option value="">Все</option>
                <option value="true">Доступна</option>
                <option value="false">Недоступна</option>
              </select>
            </div>
            <button
              type="submit"
              disabled={filtering}
              style={{ background: COLORS.brown, color: COLORS.white, border: 'none', borderRadius: 6, padding: '10px 18px', fontWeight: 600, fontSize: 15, cursor: filtering ? 'not-allowed' : 'pointer', opacity: filtering ? 0.7 : 1 }}
            >
              Найти
            </button>
            <button
              type="button"
              onClick={handleFilterReset}
              style={{ background: COLORS.white, color: COLORS.brown, border: `1px solid ${COLORS.brown}`, borderRadius: 6, padding: '10px 18px', fontWeight: 600, fontSize: 15, marginLeft: 4, cursor: filtering ? 'not-allowed' : 'pointer', opacity: filtering ? 0.7 : 1 }}
            >
              Сбросить
            </button>
          </form>
        </section>
        {/* Список книг */}
        <section>
          <div style={{ fontWeight: 600, fontSize: 20, color: COLORS.brown, marginBottom: 18 }}>Список книг</div>
          {loading && <div style={{ color: COLORS.brown, textAlign: 'center' }}>Загрузка...</div>}
          {error && <div style={{ color: COLORS.brown, textAlign: 'center' }}>Ошибка: {error}</div>}
          {!loading && !error && (
            books.length === 0 ? (
              <div style={{ color: COLORS.black, textAlign: 'center', fontSize: 18, margin: '40px 0' }}>
                Нет книг в библиотеке
              </div>
            ) : (
              <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
                {books.map((book) => (
                  <li key={book.id} style={{
                    background: COLORS.cream,
                    border: `1px solid ${COLORS.brown}`,
                    borderRadius: 10,
                    marginBottom: 20,
                    padding: 20,
                    color: COLORS.black,
                    boxShadow: '0 1px 6px #0001',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: 8,
                  }}>
                    <span style={{ fontWeight: 600, fontSize: 20 }}>{book.title}</span>
                    <span style={{ color: COLORS.brown, fontSize: 16 }}>Автор: {book.author}</span>
                    {book.description && <span style={{ fontSize: 15 }}>{book.description}</span>}
                    <span style={{ fontSize: 14, color: book.is_available ? COLORS.brown : COLORS.black }}>
                      {book.is_available ? 'Доступна для обмена' : 'Недоступна'}
                    </span>
                    <span style={{ color: COLORS.brown, fontSize: 15, fontStyle: 'italic' }}>
                      {book.owner_username ? `${book.owner_username} опубликовал эту книгу для обмена` : ''}
                    </span>
                    <div style={{ display: 'flex', gap: 8, marginTop: 8 }}>
                      <button
                        onClick={() => openReviews(book.id)}
                        style={{ background: COLORS.brown, color: COLORS.white, border: 'none', borderRadius: 6, padding: '6px 16px', fontWeight: 500, fontSize: 15, cursor: 'pointer' }}
                      >
                        Отзывы
                      </button>
                      {/* Кнопка обмена — только если книга доступна и не твоя */}
                      {book.is_available && book.owner_id !== user.id && (
                        <button
                          onClick={() => openExchange(book.id)}
                          style={{ background: COLORS.white, color: COLORS.brown, border: `1px solid ${COLORS.brown}`, borderRadius: 6, padding: '6px 16px', fontWeight: 500, fontSize: 15, cursor: 'pointer' }}
                        >
                          Запросить обмен
                        </button>
                      )}
                    </div>
                  </li>
                ))}
              </ul>
            )
          )}
        </section>
        {/* Модальное окно обмена */}
        {showExchange && (
          <div style={{ position: 'fixed', top: 0, left: 0, width: '100vw', height: '100vh', background: '#0008', zIndex: 1000, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <div style={{ background: COLORS.white, borderRadius: 14, boxShadow: '0 4px 32px #0003', padding: 32, minWidth: 340, maxWidth: 420, position: 'relative' }}>
              <button onClick={closeExchange} style={{ position: 'absolute', top: 12, right: 12, background: 'none', border: 'none', fontSize: 22, color: COLORS.brown, cursor: 'pointer' }}>&times;</button>
              <div style={{ fontWeight: 600, fontSize: 20, color: COLORS.brown, marginBottom: 10 }}>Запросить обмен</div>
              {myBooks.length === 0 ? (
                <div style={{ color: COLORS.black, fontSize: 16, margin: '18px 0' }}>У вас нет книг для обмена</div>
              ) : (
                <form onSubmit={handleExchange} style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                  <label style={{ color: COLORS.brown, fontWeight: 500, fontSize: 15 }}>Выберите свою книгу для обмена:</label>
                  <select
                    value={exchangeBookId}
                    onChange={e => setExchangeBookId(e.target.value)}
                    style={{ padding: 8, borderRadius: 6, border: `1px solid ${COLORS.brown}`, fontSize: 15 }}
                  >
                    <option value="">-- Выберите книгу --</option>
                    {myBooks.map((b) => (
                      <option key={b.id} value={b.id}>{b.title} — {b.author}</option>
                    ))}
                  </select>
                  <label style={{ color: COLORS.brown, fontWeight: 500, fontSize: 15, marginTop: 8 }}>Место обмена:</label>
                  <select
                    value={exchangePlace}
                    onChange={e => setExchangePlace(e.target.value)}
                    style={{ padding: 8, borderRadius: 6, border: `1px solid ${COLORS.brown}`, fontSize: 15 }}
                  >
                    {PLACES.map((place, idx) => (
                      <option key={idx} value={place}>{place}</option>
                    ))}
                  </select>
                  {exchangeError && <div style={{ color: 'red', fontSize: 14 }}>{exchangeError}</div>}
                  <button
                    type="submit"
                    disabled={exchangeLoading}
                    style={{ background: COLORS.brown, color: COLORS.white, border: 'none', borderRadius: 6, padding: '8px 0', fontWeight: 600, fontSize: 15, cursor: exchangeLoading ? 'not-allowed' : 'pointer', opacity: exchangeLoading ? 0.7 : 1 }}
                  >
                    {exchangeLoading ? 'Отправка...' : 'Отправить заявку'}
                  </button>
                </form>
              )}
            </div>
          </div>
        )}
        {/* Модальное окно отзывов */}
        {showReviews && (
          <div style={{ position: 'fixed', top: 0, left: 0, width: '100vw', height: '100vh', background: '#0008', zIndex: 1000, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <div style={{ background: COLORS.white, borderRadius: 14, boxShadow: '0 4px 32px #0003', padding: 32, minWidth: 340, maxWidth: 420, position: 'relative' }}>
              <button onClick={closeReviews} style={{ position: 'absolute', top: 12, right: 12, background: 'none', border: 'none', fontSize: 22, color: COLORS.brown, cursor: 'pointer' }}>&times;</button>
              <div style={{ fontWeight: 600, fontSize: 20, color: COLORS.brown, marginBottom: 10 }}>Отзывы о книге</div>
              {reviewsLoading ? (
                <div style={{ color: COLORS.brown }}>Загрузка...</div>
              ) : (
                <>
                  {reviews.length === 0 ? (
                    <div style={{ color: COLORS.black, fontSize: 16, margin: '18px 0' }}>Пока нет отзывов</div>
                  ) : (
                    <ul style={{ listStyle: 'none', padding: 0, margin: 0, marginBottom: 18 }}>
                      {reviews.map((r, idx) => (
                        <li key={idx} style={{ borderBottom: `1px solid ${COLORS.cream}`, padding: '10px 0' }}>
                          <StarRating value={r.rating} readOnly />
                          <div style={{ color: COLORS.black, fontSize: 15, margin: '4px 0 0 0' }}>{r.text}</div>
                          <div style={{ color: COLORS.brown, fontSize: 13, marginTop: 2 }}>Пользователь #{r.user_id}</div>
                        </li>
                      ))}
                    </ul>
                  )}
                  <form onSubmit={handleAddReview} style={{ display: 'flex', flexDirection: 'column', gap: 8, marginTop: 10 }}>
                    <div style={{ fontWeight: 500, color: COLORS.brown, fontSize: 15 }}>Оставить отзыв</div>
                    <StarRating value={reviewForm.rating} onChange={handleReviewRating} />
                    <textarea
                      name="text"
                      value={reviewForm.text}
                      onChange={handleReviewInput}
                      placeholder="Ваш отзыв..."
                      style={{ padding: 8, borderRadius: 6, border: `1px solid ${COLORS.brown}`, fontSize: 15, resize: 'vertical', minHeight: 50 }}
                    />
                    {reviewError && <div style={{ color: 'red', fontSize: 14 }}>{reviewError}</div>}
                    <button
                      type="submit"
                      disabled={reviewAdding}
                      style={{ background: COLORS.brown, color: COLORS.white, border: 'none', borderRadius: 6, padding: '8px 0', fontWeight: 600, fontSize: 15, cursor: reviewAdding ? 'not-allowed' : 'pointer', opacity: reviewAdding ? 0.7 : 1 }}
                    >
                      {reviewAdding ? 'Добавление...' : 'Оставить отзыв'}
                    </button>
                  </form>
                </>
              )}
            </div>
          </div>
        )}
        {/* Модалка моих заявок */}
        {showMyExchanges && (
          <div style={{ position: 'fixed', top: 0, left: 0, width: '100vw', height: '100vh', background: '#0008', zIndex: 1000, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <div style={{ background: COLORS.white, borderRadius: 14, boxShadow: '0 4px 32px #0003', padding: 32, minWidth: 340, maxWidth: 480, position: 'relative' }}>
              <button onClick={() => setShowMyExchanges(false)} style={{ position: 'absolute', top: 12, right: 12, background: 'none', border: 'none', fontSize: 22, color: COLORS.brown, cursor: 'pointer' }}>&times;</button>
              <div style={{ fontWeight: 600, fontSize: 20, color: COLORS.brown, marginBottom: 10 }}>Мои заявки на обмен</div>
              {exchangesLoading ? (
                <div style={{ color: COLORS.brown }}>Загрузка...</div>
              ) : (
                myExchanges.length === 0 ? (
                  <div style={{ color: COLORS.black, fontSize: 16, margin: '18px 0' }}>Нет отправленных заявок</div>
                ) : (
                  <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
                    {myExchanges.map((ex) => (
                      <li key={ex.id} style={{ borderBottom: `1px solid ${COLORS.cream}`, padding: '10px 0' }}>
                        <div style={{ fontWeight: 500, color: COLORS.brown }}>Книга: {ex.book_title}</div>
                        <div style={{ color: COLORS.black, fontSize: 15 }}>В обмен на: {ex.offered_book_title}</div>
                        <div style={{ color: COLORS.brown, fontSize: 14 }}>Место обмена: {ex.place}</div>
                        <div style={{ color: COLORS.brown, fontSize: 14 }}>Статус: {ex.status === 'pending' ? 'В ожидании' : ex.status === 'accepted' ? 'Принято' : 'Отклонено'}</div>
                      </li>
                    ))}
                  </ul>
                )
              )}
            </div>
          </div>
        )}
        {/* Модалка входящих заявок */}
        {showIncomingExchanges && (
          <div style={{ position: 'fixed', top: 0, left: 0, width: '100vw', height: '100vh', background: '#0008', zIndex: 1000, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <div style={{ background: COLORS.white, borderRadius: 14, boxShadow: '0 4px 32px #0003', padding: 32, minWidth: 340, maxWidth: 520, position: 'relative' }}>
              <button onClick={() => setShowIncomingExchanges(false)} style={{ position: 'absolute', top: 12, right: 12, background: 'none', border: 'none', fontSize: 22, color: COLORS.brown, cursor: 'pointer' }}>&times;</button>
              <div style={{ fontWeight: 600, fontSize: 20, color: COLORS.brown, marginBottom: 10 }}>Входящие заявки на мои книги</div>
              {exchangesLoading ? (
                <div style={{ color: COLORS.brown }}>Загрузка...</div>
              ) : (
                incomingExchanges.length === 0 ? (
                  <div style={{ color: COLORS.black, fontSize: 16, margin: '18px 0' }}>Нет входящих заявок</div>
                ) : (
                  <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
                    {incomingExchanges.map((ex) => (
                      <li key={ex.id} style={{ borderBottom: `1px solid ${COLORS.cream}`, padding: '10px 0', display: 'flex', flexDirection: 'column', gap: 6 }}>
                        <div style={{ fontWeight: 500, color: COLORS.brown }}>Книга: {ex.book_title}</div>
                        <div style={{ color: COLORS.black, fontSize: 15 }}>В обмен на: {ex.offered_book_title}</div>
                        <div style={{ color: COLORS.brown, fontSize: 14 }}>Место обмена: {ex.place}</div>
                        <div style={{ color: COLORS.brown, fontSize: 14 }}>От пользователя #{ex.user_id}</div>
                        <div style={{ color: COLORS.brown, fontSize: 14 }}>Статус: {ex.status === 'pending' ? 'В ожидании' : ex.status === 'accepted' ? 'Принято' : 'Отклонено'}</div>
                        {ex.status === 'pending' && (
                          <div style={{ display: 'flex', gap: 10, marginTop: 4 }}>
                            <button onClick={() => handleExchangeAction(ex.id, 'accept')} disabled={exchangeActionLoading} style={{ background: COLORS.green, color: COLORS.white, border: 'none', borderRadius: 6, padding: '6px 16px', fontWeight: 600, fontSize: 15, cursor: exchangeActionLoading ? 'not-allowed' : 'pointer', opacity: exchangeActionLoading ? 0.7 : 1 }}>Принять</button>
                            <button onClick={() => handleExchangeAction(ex.id, 'reject')} disabled={exchangeActionLoading} style={{ background: COLORS.red, color: COLORS.white, border: 'none', borderRadius: 6, padding: '6px 16px', fontWeight: 600, fontSize: 15, cursor: exchangeActionLoading ? 'not-allowed' : 'pointer', opacity: exchangeActionLoading ? 0.7 : 1 }}>Отклонить</button>
                          </div>
                        )}
                      </li>
                    ))}
                  </ul>
                )
              )}
            </div>
          </div>
        )}
        {/* Модалка профиля */}
        {showProfile && (
          <div style={{ position: 'fixed', top: 0, left: 0, width: '100vw', height: '100vh', background: '#0008', zIndex: 1000, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <div style={{ background: COLORS.white, borderRadius: 14, boxShadow: '0 4px 32px #0003', padding: 32, minWidth: 340, maxWidth: 600, position: 'relative' }}>
              <button onClick={() => setShowProfile(false)} style={{ position: 'absolute', top: 12, right: 12, background: 'none', border: 'none', fontSize: 22, color: COLORS.brown, cursor: 'pointer' }}>&times;</button>
              <div style={{ fontWeight: 700, fontSize: 22, color: COLORS.brown, marginBottom: 10 }}>Профиль пользователя</div>
              <div style={{ color: COLORS.black, fontSize: 17, marginBottom: 18 }}>
                <b>{user.username}</b> <span style={{ color: COLORS.brown, fontSize: 15 }}>({user.email})</span>
              </div>
              <div style={{ display: 'flex', gap: 12, marginBottom: 18 }}>
                <button onClick={() => setProfileTab('books')} style={{ background: profileTab==='books'?COLORS.brown:COLORS.cream, color: profileTab==='books'?COLORS.white:COLORS.brown, border: 'none', borderRadius: 6, padding: '8px 18px', fontWeight: 600, fontSize: 15, cursor: 'pointer' }}>Мои книги</button>
                <button onClick={() => setProfileTab('reviews')} style={{ background: profileTab==='reviews'?COLORS.brown:COLORS.cream, color: profileTab==='reviews'?COLORS.white:COLORS.brown, border: 'none', borderRadius: 6, padding: '8px 18px', fontWeight: 600, fontSize: 15, cursor: 'pointer' }}>Мои отзывы</button>
                <button onClick={() => setProfileTab('exchanges')} style={{ background: profileTab==='exchanges'?COLORS.brown:COLORS.cream, color: profileTab==='exchanges'?COLORS.white:COLORS.brown, border: 'none', borderRadius: 6, padding: '8px 18px', fontWeight: 600, fontSize: 15, cursor: 'pointer' }}>История обменов</button>
              </div>
              {profileLoading ? (
                <div style={{ color: COLORS.brown }}>Загрузка...</div>
              ) : (
                <>
                  {profileTab === 'books' && (
                    <div>
                      <div style={{ fontWeight: 600, color: COLORS.brown, marginBottom: 8 }}>Мои книги:</div>
                      {profileBooks.length === 0 ? (
                        <div style={{ color: COLORS.black, fontSize: 16 }}>Нет добавленных книг</div>
                      ) : (
                        <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
                          {profileBooks.map((b) => (
                            <li key={b.id} style={{ borderBottom: `1px solid ${COLORS.cream}`, padding: '10px 0' }}>
                              <span style={{ fontWeight: 600 }}>{b.title}</span> — <span style={{ color: COLORS.brown }}>{b.author}</span>
                              <span style={{ fontSize: 14, color: b.is_available ? COLORS.brown : COLORS.black, marginLeft: 8 }}>
                                {b.is_available ? 'Доступна' : 'Недоступна'}
                              </span>
                            </li>
                          ))}
                        </ul>
                      )}
                    </div>
                  )}
                  {profileTab === 'reviews' && (
                    <div>
                      <div style={{ fontWeight: 600, color: COLORS.brown, marginBottom: 8 }}>Мои отзывы:</div>
                      {profileReviews.length === 0 ? (
                        <div style={{ color: COLORS.black, fontSize: 16 }}>Нет отзывов</div>
                      ) : (
                        <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
                          {profileReviews.map((r, idx) => (
                            <li key={idx} style={{ borderBottom: `1px solid ${COLORS.cream}`, padding: '10px 0' }}>
                              <span style={{ fontWeight: 600 }}>{r.book_title || 'Книга'}</span>
                              <span style={{ marginLeft: 8 }}><StarRating value={r.rating} readOnly /></span>
                              <span style={{ color: COLORS.black, fontSize: 15, marginLeft: 8 }}>{r.text}</span>
                            </li>
                          ))}
                        </ul>
                      )}
                    </div>
                  )}
                  {profileTab === 'exchanges' && (
                    <div>
                      <div style={{ fontWeight: 600, color: COLORS.brown, marginBottom: 8 }}>История обменов:</div>
                      {profileExchanges.length === 0 ? (
                        <div style={{ color: COLORS.black, fontSize: 16 }}>Нет завершённых обменов</div>
                      ) : (
                        <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
                          {profileExchanges.map((ex) => (
                            <li key={ex.id} style={{ borderBottom: `1px solid ${COLORS.cream}`, padding: '10px 0' }}>
                              <span style={{ fontWeight: 600 }}>Книга: {ex.book_title}</span>
                              <span style={{ color: COLORS.black, fontSize: 15, marginLeft: 8 }}>В обмен на: {ex.offered_book_title}</span>
                              <span style={{ color: COLORS.brown, fontSize: 14, marginLeft: 8 }}>Дата: {ex.timestamp ? new Date(ex.timestamp).toLocaleString() : ''}</span>
                            </li>
                          ))}
                        </ul>
                      )}
                    </div>
                  )}
                </>
              )}
            </div>
          </div>
        )}
        {/* Модалка админ-панели */}
        {showAdmin && (
          <div style={{ position: 'fixed', top: 0, left: 0, width: '100vw', height: '100vh', background: '#0008', zIndex: 1000, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <div style={{ background: COLORS.white, borderRadius: 14, boxShadow: '0 4px 32px #0003', padding: 32, minWidth: 340, maxWidth: 900, position: 'relative', overflowY: 'auto', maxHeight: '90vh' }}>
              <button onClick={() => setShowAdmin(false)} style={{ position: 'absolute', top: 12, right: 12, background: 'none', border: 'none', fontSize: 22, color: COLORS.brown, cursor: 'pointer' }}>&times;</button>
              <div style={{ fontWeight: 700, fontSize: 22, color: COLORS.brown, marginBottom: 10 }}>Админ-панель</div>
              {adminLoading ? (
                <div style={{ color: COLORS.brown }}>Загрузка...</div>
              ) : (
                <>
                  <div style={{ display: 'flex', gap: 32, marginBottom: 24 }}>
                    <div style={{ fontWeight: 600, color: COLORS.brown }}>Пользователей: {adminStats.users}</div>
                    <div style={{ fontWeight: 600, color: COLORS.brown }}>Книг: {adminStats.books}</div>
                    <div style={{ fontWeight: 600, color: COLORS.brown }}>Обменов: {adminStats.exchanges}</div>
                  </div>
                  <div style={{ marginBottom: 18 }}>
                    <div style={{ fontWeight: 600, color: COLORS.brown, marginBottom: 6 }}>Все пользователи:</div>
                    <ul style={{ listStyle: 'none', padding: 0, margin: 0, maxHeight: 120, overflowY: 'auto' }}>
                      {adminUsers.map(u => (
                        <li key={u.id} style={{ borderBottom: `1px solid ${COLORS.cream}`, padding: '6px 0' }}>{u.username} <span style={{ color: COLORS.brown, fontSize: 14 }}>({u.email})</span></li>
                      ))}
                    </ul>
                  </div>
                  <div style={{ marginBottom: 18 }}>
                    <div style={{ fontWeight: 600, color: COLORS.brown, marginBottom: 6 }}>Все книги:</div>
                    <ul style={{ listStyle: 'none', padding: 0, margin: 0, maxHeight: 120, overflowY: 'auto' }}>
                      {adminBooks.map(b => (
                        <li key={b.id} style={{ borderBottom: `1px solid ${COLORS.cream}`, padding: '6px 0' }}>{b.title} — {b.author} <span style={{ color: COLORS.brown, fontSize: 14 }}>({b.is_available ? 'Доступна' : 'Недоступна'})</span></li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <div style={{ fontWeight: 600, color: COLORS.brown, marginBottom: 6 }}>Все обмены:</div>
                    <ul style={{ listStyle: 'none', padding: 0, margin: 0, maxHeight: 120, overflowY: 'auto' }}>
                      {adminExchanges.map(ex => (
                        <li key={ex.id} style={{ borderBottom: `1px solid ${COLORS.cream}`, padding: '6px 0' }}>
                          Книга: {ex.book_title} ⇄ {ex.offered_book_title} <span style={{ color: COLORS.brown, fontSize: 14 }}>({ex.status})</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </>
              )}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
