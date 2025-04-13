import React, { useState, useEffect } from 'react';
import './Appointments.css';
import axios from 'axios';
import { useLocation } from 'react-router-dom';
import SignaturePad from './SignaturePad';

const Appointments = () => {
  const location = useLocation();
  const params = new URLSearchParams(location.search);
  const branchId = parseInt(params.get('branch_id')) || 0;

  const [date, setDate] = useState('2025-03-10');
  const [page, setPage] = useState(1);
  const [fetchedAppointments, setFetchedAppointments] = useState([]);
  const [loading, setLoading] = useState(false);

  const [selectedAppointment, setSelectedAppointment] = useState(null);
  const [showArrivalModal, setShowArrivalModal] = useState(false);
  const [showDetailsModal, setShowDetailsModal] = useState(false);
  const [showSignatureModal, setShowSignatureModal] = useState(false);

  const itemsPerPage = 5;
  const totalPages = Math.ceil(fetchedAppointments.length / itemsPerPage);
  const displayedAppointments = fetchedAppointments.slice((page - 1) * itemsPerPage, page * itemsPerPage);

  const isAdmin = branchId === 0;

  const fetchAppointments = async () => {
    setLoading(true);
    try {
      const res = await axios.get('http://localhost:5000/api/appointments', {
        params: {
          branch_id: branchId,
          appointment_date: date,
        },
      });
      console.log("🔄 Updated appointments:", res.data);
      setFetchedAppointments(res.data);
    } catch (err) {
      console.error('❌ Error fetching appointments', err);
      setFetchedAppointments([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAppointments();
  }, [branchId, date]);

  const changeDateBy = (days) => {
    const current = new Date(date);
    current.setDate(current.getDate() + days);
    setDate(current.toISOString().split('T')[0]);
    setPage(1);
  };

  const handleDateChange = (e) => {
    setDate(e.target.value);
    setPage(1);
  };

  const handleRowClick = (appt) => {
    setSelectedAppointment(appt);
    setShowArrivalModal(true);
  };

  const handleConfirmYes = async () => {
    setShowArrivalModal(false);
    setShowDetailsModal(true);
  };

  return (
    <div className="appointments-container" dir="rtl">
      <h2>רשימת רכבים צבאיים לתאריך</h2>

      <div className="date-controls">
        <button onClick={() => changeDateBy(-1)}>🔽</button>
        <input type="date" value={date} onChange={handleDateChange} className="date-input" />
        <button onClick={() => changeDateBy(1)}>🔼</button>
      </div>

      <div className="appointments-table">
        <div className="table-header">
          <div>מס' פניה</div>
          <div>שעה</div>
          <div>מספר רכב</div>
          <div>שם נהג</div>
          <div>{isAdmin ? 'פנצריה' : "טל' נהג"}</div>
        </div>

        <div className="table-body">
          {Array.from({ length: itemsPerPage }).map((_, idx) => {
            const appt = displayedAppointments[idx];
            const isCompleted = appt?.AppointmentActualSet === 1;

            const rowClass = isCompleted ? 'table-row completed-row' : 'table-row';

            return (
              <div
                key={idx}
                className={rowClass}
                onClick={() => {
                  if (!isCompleted && appt && !isAdmin) handleRowClick(appt);
                }}
                style={{ cursor: !isAdmin && !isCompleted ? 'pointer' : 'default' }}
              >
                <div>{appt?.AppointmentID || ' '}</div>
                <div>{appt?.AppointmentTime?.slice(0, 5) || ' '}</div>
                <div>{appt?.CarNum || ' '}</div>
                <div>{appt?.DriverName || ' '}</div>
                <div>{isAdmin ? (appt?.Name || ' ') : (appt?.DriverPhone || ' ')}</div>
              </div>
            );
          })}
        </div>
      </div>

      {fetchedAppointments.length > 0 && (
        <div className="pagination-controls">
          <button
            className="pagination-btn"
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page === 1}
          >
            ←
          </button>
          <span className="pagination-info">
            עמוד {page} מתוך {totalPages}
          </span>
          <button
            className="pagination-btn"
            onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
            disabled={page === totalPages}
          >
            →
          </button>
        </div>
      )}

      {showArrivalModal && selectedAppointment && (
        <div className="modal-overlay">
          <div className="modal-box">
            <h3 className="modal-question">האם הגיע לטיפול?</h3>
            <div className="modal-buttons">
              <button className="yes" onClick={handleConfirmYes}>כן</button>
              <button className="no" onClick={() => setShowArrivalModal(false)}>לא</button>
            </div>
          </div>
        </div>
      )}

      {showDetailsModal && selectedAppointment && (
        <div className="modal-overlay">
          <div className="details-modal-box">
            <h3>מספר פניה - {selectedAppointment.AppointmentID}</h3>
            <div className="details-form">
              {[{ label: 'מספר רכב', value: selectedAppointment.CarNum }, { label: 'סוג רכב', value: selectedAppointment.TypeOfCar }, { label: 'נהג', value: selectedAppointment.DriverName }, { label: 'קילומטר', value: selectedAppointment.Kil }, { label: 'פעולה לביצוע', value: selectedAppointment.WorkTypeDes }, { label: 'כמות', value: selectedAppointment.Quantity }].map((field, i) => (
                <div className="details-row" key={i}>
                  <label>{field.label}</label>
                  <input value={field.value || ''} readOnly />
                </div>
              ))}
              {selectedAppointment.MikomDes?.split(',').map((mikom, index) => (
                <div className="details-row" key={index}>
                  <label>מיקום - {index + 1}</label>
                  <input value={mikom.trim()} readOnly />
                </div>
              ))}
              <div style={{ marginTop: '40px', display: 'flex', justifyContent: 'center' }}>
                <button className="sign-button" onClick={() => setShowSignatureModal(true)}>
                  חתימה
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {showSignatureModal && (
        <div className="modal-overlay">
          <SignaturePad
            onCancel={() => setShowSignatureModal(false)}
            onConfirm={async (signatureBase64) => {
              try {
                await axios.post('http://localhost:5000/api/set-signature', {
                  AppointmentID: selectedAppointment.AppointmentID,
                  Signeture: signatureBase64,
                });
                await fetchAppointments();
                setShowSignatureModal(false);
                setShowDetailsModal(false);
              } catch (err) {
                console.error("❌ Error saving signature", err);
              }
            }}
          />
        </div>
      )}
    </div>
  );
};

export default Appointments;
