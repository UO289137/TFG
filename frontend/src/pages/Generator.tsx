import React, { Fragment, useState, useEffect } from 'react';
import TextRemove from '../components/Icons/TextRemove';
import PenIcon from '../components/Icons/PenIcon';
import Slider from '@mui/material/Slider';
import SettingsIcon from '../components/Icons/SettingsIcon';
import TopBar from '../components/TopBar';
import GeneratorIcon from '../components/Icons/GeneratorIcon';
import GeneratorSelect from '../components/generator/Select';
import GoldIcon from '../components/Icons/GoldIcon';
import YdataIcon from '../components/Icons/YdataIcon';
import { useNavigate, useSearchParams } from 'react-router-dom';

const Generator: React.FC = () => {
  const [searchParams] = useSearchParams();
  const model = searchParams.get('model') || 'merlin'; // fallback a 'merlin'
  const navigate = useNavigate();

  // Estados para "rows", texto, carga, tiempo y el archivo (para ydata)
  const [rows, setRows] = useState(70);
  const [text, setText] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [elapsedTime, setElapsedTime] = useState(0);

  // Definir los rangos para cada modelo
  const rowRanges = {
    merlin: { min: 1, max: 100000 },
    gold: { min: 1, max: 200 },
    ydata: { min: 1, max: 50 },
  } as const;

  const { min, max } = rowRanges[model as keyof typeof rowRanges] || {
    min: 1,
    max: 100,
  };

  // Ajusta el valor de "rows" si está fuera del rango
  useEffect(() => {
    if (rows < min) setRows(min);
    if (rows > max) setRows(max);
  }, [model, rows, min, max]);

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

  // Manejador para la subida de archivo (para ydata)
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
    }
  };

  // Función para enviar la solicitud al backend
  const handleGenerate = async () => {
    if (model === 'ydata') {
      if (!file) {
        alert('Por favor, selecciona un archivo CSV.');
        return;
      }
    } else if (!text.trim()) {
      alert('Please enter a theme.');
      return;
    }

    setLoading(true);
    try {
      let response;
      if (model === 'ydata') {
        const formData = new FormData();
        formData.append('generator_type', model);
        formData.append('file', file as Blob);
        formData.append('rows', rows.toString());

        response = await fetch('http://localhost:5000/generate', {
          method: 'POST',
          body: formData,
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
        });
      }

      if (!response.ok) {
        throw new Error('Error generating data');
      }

      // Descarga del archivo generado
      const blob = await response.blob();
      const downloadUrl = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = downloadUrl;
      a.download = 'synthetic_data.csv';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    } catch (error) {
      console.error(error);
      alert('Error generating data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Fragment>
      {/* Top Bar */}
      <TopBar containerClassName="justify-between">
        <aside className="flex justify-start items-center gap-3">
          <GeneratorIcon className="fill-[#414042] w-[26px] h-[23.59px]" />
          <h2 className="text-[26px] font-primary font-medium">
            The Generator
          </h2>
        </aside>
      </TopBar>

      {/* Generator Bar */}
      <div className="flex justify-between items-center w-full">
        <div className="flex items-center gap-3">
          <p className="sm:text-sm text-xs text-[#414042]">Model</p>
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
                      value: 'ydata',
                      label: 'Ydata Generator',
                      Icon: YdataIcon,
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
            Tabular Data
          </button>
        </div>
      </div>

      {/* Contenido del Generator */}
      <div className="grid grid-cols-8 gap-6 mt-4">
        <div className="flex flex-col gap-3 w-full xl:col-span-6 col-span-8">
          <div className="border border-generator rounded-[5px] relative p-4">
            {model === 'ydata' ? (
              <div>
                <label className="block mb-2 text-[#414042]">
                  Selecciona un archivo CSV:
                </label>
                <input
                  type="file"
                  accept=".csv"
                  onChange={handleFileChange}
                  className="w-full"
                />
              </div>
            ) : (
              <div className="relative">
                <textarea
                  value={text}
                  onChange={(e) => setText(e.target.value)}
                  placeholder="Write an explanation about the topic you want to generate data about and its fields...."
                  className="min-h-[200px] md:min-h-[260px] w-full h-full bg-transparent outline-none border-none md:text-sm text-xs text-[#414042] placeholder:text-[#414042] resize-none overflow-hidden"
                />
                <button
                  className="absolute top-0 right-0 z-10"
                  onClick={() => setText('')}
                >
                  <TextRemove className="w-[30px] h-[30px] fill-generator relative" />
                </button>
              </div>
            )}
            <aside className="flex justify-end">
              <button
                className="bg-generator lg:py-2 py-1.5 lg:px-6 px-5 md:text-sm text-xs rounded-lg text-white font-primary flex justify-center items-center gap-2 whitespace-nowrap"
                onClick={handleGenerate}
                disabled={loading}
              >
                <PenIcon className="md:w-[22px] w-[20px] md:h-[22px] h-[20px] fill-white" />
                {loading ? `Generating... (${elapsedTime}s)` : 'Generate'}
              </button>
            </aside>
          </div>

          {/* Output */}
          <h2 className="text-[#414042] lg:text-[20px] text-[18px] font-primary font-semibold">
            Output
          </h2>
          <div className="flex flex-col items-center flex-grow lg:min-h-[200px] min-h-[150px] border border-generator rounded-[5px] justify-center">
            <img
              src="/logo-icon.png"
              alt="logo"
              className="object-contain lg:w-[70px] w-[60px] lg:h-[70px] h-[60px] pointer-events-none"
            />
            <h3 className="text-[#414042] lg:text-base text-sm font-semibold">
              Not Result Yet
            </h3>
            <p className="text-[#414042] lg:text-sm text-xs font-primary">
              The Generation is being performed
            </p>
          </div>
        </div>

        {/* Panel de configuración (solo Rows) */}
        <div className="col-span-8 xl:col-span-2">
          <span
            className="flex items-center justify-start gap-2 text-[#414042] md:text-[16px] text-sm mt-3 xl:mt-0 font-[400] rounded-[10px] p-2 text-center"
            style={{ background: 'var(--generator-light-color)' }}
          >
            <SettingsIcon className="w-[14px] h-[14px] stroke-[#414042]" />
            Settings
          </span>
          <div className="mt-3">
            <div>
              <span className="flex items-center justify-between md:text-base text-sm">
                Rows
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

            <div className="mt-4 border-t pt-2">
              <h3 className="md:text-base text-sm font-semibold text-gray-700">
                Examples
              </h3>
              <ul className="mt-2 space-y-2">
                {[
                  'Genera datos sobre los pacientes de un hospital. Quiero que añadas un identificador, grupo sanguineo, nombre, nacionalidad y enfermedad.',
                  'Genera datos sobre jugadores de baloncesto reales. Dame su nombre, edad, fecha de nacimiento, altura y una breve descripción.',
                  'Genera datos sobre una empresa. Dame el nombre de los empleados, departamento, salario y fecha de contratación. Quiero que exista una relación coherente entre el salario y los demás campos.',
                  'Genera datos de actualidad sobre las noticias en el mundo. Quiero el título de la noticia, fecha y breve descripción.',
                  'Dame los mejores lugares para ver en la ciudad de Budapest. Quiero que me des el nombre del lugar, ubicación, año de referencia y breve historia.',
                ].map((item, index) => (
                  <li
                    key={index}
                    className="flex items-center gap-2 md:text-sm text-xs text-gray-700"
                  >
                    {item}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </div>
    </Fragment>
  );
};

export default Generator;
