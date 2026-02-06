import { useEffect, useState } from 'react';

import DjangoNegativeLogoSrc from '../../assets/images/django-logo-negative.png';
import DjangoPositiveLogoSrc from '../../assets/images/django-logo-positive.png';
import { type RestRestCheckRetrieveResponse, restRestCheckRetrieve } from '../api';

const Home = () => {
  const [showBugComponent, setShowBugComponent] = useState(false);
  const [restCheck, setRestCheck] = useState<RestRestCheckRetrieveResponse>();

  useEffect(() => {
    async function onFetchRestCheck() {
      const response = await restRestCheckRetrieve();
      setRestCheck(response.data);
    }
    onFetchRestCheck();
  }, []);

  return (
    <section className="space-y-6">
      <h2 className="text-2xl font-semibold tracking-tight text-slate-900">Static assets</h2>
      <div className="space-y-4 rounded-2xl border border-slate-300 bg-white p-6 shadow-sm">
        <p className="text-[11pt] text-[#092e20]">
          If you are seeing the green Django logo on a white background and this text color is
          #092e20, frontend static files serving is working:
        </p>
        <div
          className="h-[300px] w-full rounded-xl bg-white bg-center bg-no-repeat"
          style={{ backgroundImage: `url(${DjangoPositiveLogoSrc})`, backgroundSize: 'auto 200px' }}
        />
        <div className="space-y-3 text-[#092e20]">
          <p>
            Below this text, you should see an img tag with the white Django logo on a green
            background:
          </p>
          <img alt="Django Negative Logo" className="w-[100px]" src={DjangoNegativeLogoSrc} />
        </div>
      </div>

      <h2 className="text-2xl font-semibold tracking-tight text-slate-900">Rest API</h2>
      <div className="space-y-4 rounded-2xl border border-slate-300 bg-white p-6 shadow-sm">
        <p className="text-slate-700">{restCheck?.message}</p>
        <button
          className="inline-flex items-center rounded-lg border border-slate-900 px-4 py-2 text-sm font-semibold text-slate-900 transition hover:bg-slate-900 hover:text-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-slate-400 focus-visible:ring-offset-2"
          onClick={() => setShowBugComponent(true)}
          type="button"
        >
          Click to test if Sentry is capturing frontend errors! (Should only work in Production)
        </button>
      </div>

      {/* NOTE: The next line intentionally contains an error for testing frontend errors in Sentry. */}
      {showBugComponent && (showBugComponent as any).field.notexist}
    </section>
  );
};

export default Home;
