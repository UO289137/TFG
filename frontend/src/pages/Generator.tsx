import React, { Fragment, useState, useEffect, useRef } from 'react';
import TextRemove from '../components/Icons/TextRemove';
import PenIcon from '../components/Icons/PenIcon';
import Slider from '@mui/material/Slider';
import SettingsIcon from '../components/Icons/SettingsIcon';
import TopBar from '../components/TopBar';
import GeneratorIcon from '../components/Icons/GeneratorIcon';
import GeneratorSelect from '../components/generator/Select';
import GoldIcon from '../components/Icons/GoldIcon';
import RealIcon from '../components/Icons/RealIcon';
import CtganIcon from '../components/Icons/CtganIcon';
import GaussianIcon from '../components/Icons/GaussianIcon';
import { useNavigate, useSearchParams } from 'react-router-dom';
import Papa from 'papaparse';

const Generator: React.FC = () => {
  const [searchParams] = useSearchParams();
  const model = searchParams.get('model') || 'merlin'; // fallback a 'merlin'
  const navigate = useNavigate();

  // Estados para "rows", texto, carga, tiempo y el archivo (para ctgan)
  const [rows, setRows] = useState(70);
  const [text, setText] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [elapsedTime, setElapsedTime] = useState(0);
  const [csvContent, setCsvContent] = useState<string>('');
  const [downloadEnabled, setDownloadEnabled] = useState(false);
  const [fileName, setFileName] = useState('synthetic_data');
  const [fileNameError, setFileNameError] = useState('');
  const [themeError, setThemeError] = useState('');
  const [fileError, setFileError] = useState<string>('');
  const [generalError, setGeneralError] = useState<string>('');

  // Definir los rangos para cada modelo
  const rowRanges = {
    merlin: { min: 1, max: 10000 },
    gold: { min: 1, max: 100 },
    real: { min: 1, max: 100 },
    ctgan: { min: 1, max: 10000 },
    gaussian: { min: 1, max: 10000 },
  } as const;

  const { min, max } = rowRanges[model as keyof typeof rowRanges] || {
    min: 1,
    max: 100,
  };

  const fileInputRef = useRef<HTMLInputElement>(null);

  // Ajusta el valor de "rows" si está fuera del rango
  useEffect(() => {
    if (rows < min) setRows(min);
    if (rows > max) setRows(max);
  }, [model, rows, min, max]);

  useEffect(() => {
    setRows(1);
    setText('');
    setThemeError('');
    setDownloadEnabled(false);
    setCsvContent('');
    setGeneralError('');
    setFileError('');
  }, [model]);

  // Manejador del Slider
  const handleRows = (_event: Event, newValue: number | number[]) => {
    setRows(newValue as number);
  };

  // Lleva la cuenta del tiempo transcurrido cuando está loading
  useEffect(() => {
    let timer: NodeJS.Timeout;
    if (loading) {
      setElapsedTime(0);
      timer = setInterval(() => {
        setElapsedTime((prev) => prev + 1);
      }, 1000);
    } else {
      setElapsedTime(0);
    }
    return () => {
      if (timer) clearInterval(timer);
    };
  }, [loading]);

  // Manejador para la subida de archivo (para ctgan)
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setGeneralError('');
    setFileError('');
    if (e.target.files && e.target.files.length > 0) {
      const selectedFile = e.target.files[0];
      const fileName = selectedFile.name.toLowerCase();
      // Validación de extensión .csv
      if (!fileName.endsWith('.csv')) {
        setFileError('Por favor, selecciona un archivo con extensión .csv.');
        e.target.value = '';
        setFile(null);
        return;
      }
      // Validación del contenido del CSV: al menos 2 muestras de datos (excluyendo la cabecera)
      Papa.parse(selectedFile, {
        complete: (results) => {
          // Si se ignoran líneas vacías, conviene usar skipEmptyLines: true en la configuración
          // y luego filtrar el arreglo si es necesario.
          const totalFilas = results.data.length;
          // Se asume que la primera línea es la cabecera.
          if (totalFilas - 1 < 2) {
            setFileError(
              'El CSV debe tener al menos 2 filas de datos (sin contar la cabecera).'
            );
            e.target.value = '';
            setFile(null);
            return;
          }
          // Si pasa las validaciones, se guarda el archivo
          setFile(selectedFile);
        },
        error: (error) => {
          alert('Error al procesar el archivo CSV: ' + error.message);
          e.target.value = ''; // Reiniciar input en caso de error en la lectura
          setFile(null);
        },
        // Opcional: Ignorar líneas vacías
        skipEmptyLines: true,
      });
    }
  };

  const handleGenerate = async () => {
    setGeneralError('');
    setFileError('');
    if (model === 'ctgan' || model === 'gaussian') {
      if (!file) {
        setFileError('Debes seleccionar un archivo CSV antes de generar.');
        return;
      }
    } else if (!text.trim()) {
      setThemeError('Por favor, introduce un tema.');
      return;
    }
    setLoading(true);
    // Crear un AbortController para poder cancelar la petición
    const controller = new AbortController();
    const timeoutId = setTimeout(() => {
      controller.abort();
    }, 300000); // 300000 ms = 300 segundos
    try {
      let response;
      if (model === 'ctgan' || model === 'gaussian') {
        const formData = new FormData();
        formData.append('generator_type', model);
        formData.append('file', file as Blob);
        formData.append('rows', rows.toString());
        response = await fetch('http://localhost:5000/generate', {
          method: 'POST',
          body: formData,
          signal: controller.signal, // Asociar la señal al fetch
        });
      } else {
        const payload = {
          generator_type: model,
          theme: text,
          rows: rows,
        };
        response = await fetch('http://localhost:5000/generate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
          signal: controller.signal, // Asociar la señal al fetch
        });
      }
      if (!response.ok) {
        throw new Error('Error generating data');
      }
      // Obtén el blob, conviértelo a texto y guárdalo en el estado:
      const blob = await response.blob();
      const textData = await blob.text();
      setCsvContent(textData);
      // Para la descarga, recrea el blob ya que .text() lo consume:
      if (downloadEnabled) {
        const downloadBlob = new Blob([textData], { type: 'text/csv' });
        const downloadUrl = window.URL.createObjectURL(downloadBlob);
        const a = document.createElement('a');
        a.href = downloadUrl;
        a.download = `${fileName}.csv`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
      }
    } catch (error: any) {
      if (error.name === 'AbortError') {
        // Si la petición se aborta por timeout, notificamos al usuario
        setGeneralError(
          'La petición superó el tiempo máximo de espera. Inténtalo más tarde.'
        );
      } else {
        console.error(error);
        setGeneralError(
          'Error al generar datos. Por favor, vuelve a intentarlo.'
        );
      }
    } finally {
      // al acabar: resetea el input y el estado
      setFile(null);
      setLoading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
      clearTimeout(timeoutId);
    }
  };

  return (
    <Fragment>
      {/* Top Bar */}
      <TopBar containerClassName="justify-between">
        <aside className="flex justify-start items-center gap-3">
          <GeneratorIcon className="fill-[#414042] w-[26px] h-[23.59px]" />
          <h2 className="text-[26px] font-primary font-medium">El Generador</h2>
        </aside>
      </TopBar>

      {/* Generator Bar */}
      <div className="flex justify-between items-center w-full">
        <div className="flex items-center gap-3">
          <p className="text-[#414042] lg:text-[20px] text-[18px] font-primary font-semibold">
            Modelo:
          </p>
          <div className="flex">
            <GeneratorSelect
              options={[
                {
                  label: 'Models',
                  options: [
                    {
                      value: 'merlin',
                      label: 'Merlin Generator',
                      Icon: GeneratorIcon,
                    },
                    {
                      value: 'gold',
                      label: 'Gold Generator',
                      Icon: GoldIcon,
                    },
                    {
                      value: 'real',
                      label: 'Real Generator',
                      Icon: RealIcon,
                    },
                    {
                      value: 'ctgan',
                      label: 'CTGAN Generator',
                      Icon: CtganIcon,
                    },
                    {
                      value: 'gaussian',
                      label: 'Gaussian Generator',
                      Icon: GaussianIcon,
                    },
                  ],
                },
              ]}
            />
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            className="md:py-2 p-1.5 md:px-3 px-2 border border-generator text-generator text-[#414042] lg:text-base md:text-sm text-xs"
            onClick={() => navigate('?model=merlin')}
          >
            Datos Tabulares
          </button>
        </div>
      </div>

      {/* Contenido del Generator */}
      <div className="grid grid-cols-8 gap-6 mt-4">
        <div className="flex flex-col gap-3 w-full xl:col-span-6 col-span-8">
          <div className="border border-generator rounded-[5px] relative p-4">
            {model === 'ctgan' || model === 'gaussian' ? (
              <div>
                <label htmlFor="csvFile" className="block mb-2 text-[#414042]">
                  Selecciona un archivo CSV:
                </label>
                <input
                  ref={fileInputRef}
                  id="csvFile"
                  type="file"
                  accept=".csv"
                  onChange={handleFileChange}
                  className="w-full"
                />
                {fileError && (
                  <p className="text-xs text-red-500 mt-1">{fileError}</p>
                )}
              </div>
            ) : (
              <div className="relative">
                <textarea
                  value={text}
                  onChange={(e) => {
                    setText(e.target.value);
                    if (e.target.value.trim() !== '') {
                      setThemeError('');
                    }
                  }}
                  maxLength={500}
                  placeholder="Describe la temática y estructura que quieres que tengan tus datos."
                  className="min-h-[200px] md:min-h-[260px] w-[93%] h-full bg-transparent outline-none border-none md:text-sm text-xs text-[#414042] placeholder:text-[#414042] resize-none overflow-hidden"
                />
                {/* Contador de caracteres en la parte inferior del textarea */}
                <p className="text-xs text-gray-500 mt-1 text-right">
                  {text.length} / 500 caracteres
                </p>
                {themeError && (
                  <p className="text-xs text-red-500 mt-1">{themeError}</p>
                )}
                <button
                  aria-label="Borrar texto"
                  title="Borrar texto"
                  className="absolute top-0 right-0 z-10"
                  onClick={() => setText('')}
                >
                  <TextRemove className="w-[30px] h-[30px] fill-generator relative" />
                </button>
              </div>
            )}
            <aside className="flex justify-end">
              <button
                className={`lg:py-2 py-1.5 lg:px-6 px-5 md:text-sm text-xs rounded-lg font-primary flex justify-center items-center gap-2 whitespace-nowrap ${
                  loading || (downloadEnabled && fileNameError !== '')
                    ? 'bg-gray-400 cursor-not-allowed text-black'
                    : 'bg-generator text-white'
                }`}
                onClick={handleGenerate}
                disabled={loading || (downloadEnabled && fileNameError !== '')}
              >
                <PenIcon className="md:w-[22px] w-[20px] md:h-[22px] h-[20px] fill-white" />
                {loading ? `Generating... (${elapsedTime}s)` : 'Generar'}
              </button>
            </aside>
            {generalError && (
              <div className="text-xs text-red-500 mt-1">{generalError}</div>
            )}
          </div>

          {/* Output */}
          <h2 className="text-[#414042] lg:text-[20px] text-[18px] font-primary font-semibold">
            Salida:
          </h2>
          <div className="flex flex-col items-center border border-generator rounded-[5px] justify-center p-4 overflow-y-auto max-h-[323px]">
            {loading ? (
              <div className="flex flex-col items-center">
                <div className="w-8 h-8 border-4 border-t-4 border-t-generator rounded-full animate-spin mb-2"></div>
                <p className="text-[#414042] lg:text-sm text-xs font-primary">
                  Cargando ...
                </p>
              </div>
            ) : csvContent ? (
              <div className="w-full overflow-x-auto">
                {(() => {
                  // Parseamos el CSV usando PapaParse
                  const parsedData = Papa.parse(csvContent, {
                    header: false,
                  }).data;
                  // Verificamos que se obtuvo al menos una fila para el encabezado
                  if (!parsedData || parsedData.length === 0) {
                    return <p>No se pudo parsear el CSV.</p>;
                  }
                  return (
                    <table className="min-w-full table-fixed border-collapse border border-gray-300">
                      <thead className="bg-gray-200 sticky top-0 z-10">
                        <tr>
                          {parsedData[0].map((headerCell, idx) => (
                            <th
                              key={idx}
                              className="border border-gray-300 p-2 text-left font-bold w-[150px] truncate"
                            >
                              {headerCell}
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {parsedData.slice(1, 2001).map((row, rowIndex) => {
                          // Verificamos que la fila no esté vacía
                          if (row.every((cell) => cell.trim() === ''))
                            return null;
                          return (
                            <tr key={rowIndex} className="hover:bg-gray-50">
                              {row.map((cell, cellIndex) => (
                                <td
                                  key={cellIndex}
                                  className="border border-gray-300 p-2"
                                  style={{
                                    height: '50px', // Fija la altura de la celda
                                    whiteSpace: 'nowrap', // Fuerza que el contenido se mantenga en una línea
                                    overflow: 'visible', // Permite que el contenido se muestre completo
                                  }}
                                >
                                  {cell}
                                </td>
                              ))}
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  );
                })()}
              </div>
            ) : (
              <>
                <h3 className="text-[#414042] lg:text-base text-sm font-semibold">
                  No hay resultados todavía
                </h3>
                <p className="text-[#414042] lg:text-sm text-xs font-primary">
                  La generación aún no ha sido realizada
                </p>
              </>
            )}
          </div>
        </div>

        {/* Panel de configuración (solo Rows) */}
        <div className="col-span-8 xl:col-span-2">
          <span className="flex items-center justify-start gap-2 text-[#414042] md:text-[16px] text-sm mt-3 xl:mt-0 font-[400] rounded-[10px] p-2 text-center bg-generator text-white">
            <SettingsIcon className="w-[14px] h-[14px] stroke-[#414042] stroke-white" />
            Ajustes
          </span>
          <div className="mt-3">
            <div>
              <span className="flex items-center justify-between md:text-base text-sm font-semibold">
                Filas
                <label className="p-1 bg-slate-50 rounded-md border lg:px-4 px-3 lg:py-1 py-0.8 lg:text-sm text-xs font-light">
                  {rows}
                </label>
              </span>
              <Slider
                value={rows}
                onChange={handleRows}
                min={min}
                max={max}
                aria-label="Rows"
                sx={{
                  color: '#1E647F',
                  '& .MuiSlider-thumb': {
                    backgroundColor: '#1E647F',
                    width: { xs: 14, md: 16 },
                    height: { xs: 14, md: 16 },
                  },
                  '& .MuiSlider-track': { backgroundColor: '#1E647F' },
                  '& .MuiSlider-rail': { backgroundColor: '#1E647F66' },
                }}
              />
            </div>
            <div className="mt-4">
              <div className="flex items-center justify-between">
                <span className="md:text-base text-sm text-[#414042] font-semibold">
                  Descargar archivo
                </span>
                <button
                  onClick={() => setDownloadEnabled(!downloadEnabled)}
                  className={`w-10 h-6 rounded-full ${
                    downloadEnabled ? 'bg-generator' : 'bg-gray-300'
                  } relative focus:outline-none`}
                  aria-label="Descargar archivo"
                  title="Descargar archivo"
                >
                  <span
                    className={`absolute w-4 h-4 bg-white rounded-full top-1 transition-all ${
                      downloadEnabled ? 'right-1' : 'left-1'
                    }`}
                  ></span>
                </button>
              </div>
              {downloadEnabled && (
                <div className="mt-2">
                  <label
                    className="block text-[#414042] md:text-base text-sm"
                    style={{ fontSize: '14px' }}
                    htmlFor="textInput"
                  >
                    Nombre del archivo (sin extensión):
                  </label>
                  <input
                    id="textInput"
                    type="text"
                    value={fileName}
                    onChange={(e) => {
                      const newName = e.target.value;
                      if (newName.trim() === '') {
                        setFileNameError('El nombre no puede estar vacío');
                      } else if (!/^[a-zA-Z0-9-_]+$/.test(newName)) {
                        setFileNameError(
                          'El nombre solo puede contener letras, números, guiones y guiones bajos'
                        );
                      } else {
                        setFileNameError('');
                      }
                      setFileName(newName);
                    }}
                    className="mt-1 p-2 border rounded-md w-full"
                  />
                  {fileNameError && (
                    <p className="text-xs text-red-500 mt-1">{fileNameError}</p>
                  )}
                </div>
              )}
            </div>

            <div className="mt-4 border-t pt-2">
              <h3 className="md:text-base text-sm font-semibold text-gray-700">
                Ejemplos
              </h3>
              <div className="mt-2">
                {[
                  'Genera datos sobre los pacientes de un hospital. Quiero que añadas un identificador, grupo sanguineo, nombre, nacionalidad y enfermedad.',
                  'Genera datos sobre jugadores de baloncesto reales. Dame su nombre, edad, fecha de nacimiento, altura y una breve descripción.',
                  'Genera datos sobre una empresa. Dame el nombre de los empleados, departamento, salario y fecha de contratación. Quiero que exista una relación coherente entre el salario y los demás campos.',
                  'Genera datos de actualidad sobre las noticias en el mundo. Quiero el título de la noticia, fecha y breve descripción.',
                  'Dame los mejores lugares para ver en la ciudad de Budapest. Quiero que me des el nombre del lugar, ubicación, año de referencia y breve historia.',
                ].map((item, index, arr) => (
                  <div key={index}>
                    <ul className="mt-2">
                      <li className="md:text-sm text-xs text-gray-700 py-2">
                        {item}
                      </li>
                    </ul>
                    {/* Insertar el <hr> entre los elementos, no después del último */}
                    {index < arr.length - 1 && (
                      <hr className="border-t border-gray-300 my-2" />
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </Fragment>
  );
};

export default Generator;
