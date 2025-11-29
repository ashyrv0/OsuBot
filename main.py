import win32api
import time
import keyboard
from getmap import get_active_map_name, find_map_directory, find_read_data
import win32gui


class Relaxer:
    def __init__(self):
        self.alternated = False
        self.maptext = None
        self.timing_points = []
        self.slider_mult = 1.0
        self.hits_array = []
        self.base_time = None

    def tabbedin(self):
        return "osu!" in win32gui.GetWindowText(win32gui.GetForegroundWindow())

    def parse_timing_points(self, text):
        pts = []
        s = text.find("[TimingPoints]")
        if s == -1:
            return pts
        block = text[s + len("[TimingPoints]"):]
        i = block.find("\n[")
        if i != -1:
            block = block[:i]
        for line in block.splitlines():
            line = line.strip()
            if not line or line.startswith("//"):
                continue
            p = line.split(",")
            try:
                t = int(float(p[0]))
                bl = float(p[1])
                unin = int(p[6]) if len(p) > 6 else 1
                pts.append({"time": t, "beatLength": bl, "uninherited": unin})
            except:
                continue
        pts.sort(key=lambda x: x["time"])
        return pts
        
    def get_slider_multiplier(self, text):
        for line in text.splitlines():
            line = line.strip()
            if line.startswith("SliderMultiplier:"):
                try:
                    return float(line.split(":")[1].strip())
                except:
                    return 1.0
        return 1.0

    def slider_duration_sec(self, length_px, slides, t_ms, slider_mult, timing_points):
        beat = None 
        for tp in reversed(timing_points):
            if tp["time"] <= t_ms and tp["uninherited"] == 1:
                beat = tp["beatLength"]
                break
        if beat is None:
            beat = timing_points[0]["beatLength"] if timing_points else 500.0
        inh = None
        for tp in reversed(timing_points):
            if tp["time"] <= t_ms and tp["uninherited"] == 0:
                inh = tp["beatLength"]
                break
        sv = (-100 / inh) if inh is not None and inh != 0 else 1.0
        per_slide_ms = length_px / (slider_mult * 100.0 * sv) * beat
        return (per_slide_ms * max(1, slides)) / 1000.0

    def click_hold(self, duration_s, key):
        win32api.keybd_event(key, 0, 0, 0)
        time.sleep(duration_s)
        win32api.keybd_event(key, 0, 2, 0)

    def load_map(self):
        print("Press enter to get map")
        keyboard.wait('enter')
        
        window_title = get_active_map_name()
        print(f"Window title: {window_title}")
        
        song_info = window_title.replace("osu! - ", "").replace("osu!  - ", "")
        if "[" in song_info and "]" in song_info:
            start = song_info.rfind("[")
            end = song_info.rfind("]")
            diff_name = song_info[start+1:end]
            song_name = song_info[:start].strip()
        else:
            diff_name = ""
            song_name = song_info
        
        print(f"Song name: {song_name}")
        print(f"Looking for difficulty: {diff_name}")
        
        # Find the map directory using the song name
        map_dir = find_map_directory(song_name)
        
        if map_dir is None:
            print("Error: Could not find map directory!")
            print(f"Searched for: {song_name}")
            return
        
        print(f"Found map directory: {map_dir}")
        
        # Read the .osu file content
        self.maptext = find_read_data(map_dir, diff_name)
        
        if self.maptext is None:
            print("Error: Could not read .osu file!")
            return
        
        print("Map loaded successfully!")
        self.timing_points = self.parse_timing_points(self.maptext)
        self.slider_mult = self.get_slider_multiplier(self.maptext)
    
    def parse_hit_objects(self):
        raw = []
        s = self.maptext.find("[HitObjects]")
        if s != -1:
            block = self.maptext[s + len("[HitObjects]"):]
            i = block.find("\n[")
            if i != -1:
                block = block[:i]
            for L in [l.strip() for l in block.splitlines() if l.strip() and not l.strip().startswith("//")]:
                p = L.split(",")
                if len(p) < 3:
                    continue
                try:
                    x = int(p[0])
                    y = int(p[1])
                    t = int(p[2])
                except:
                    continue
                if len(p) >= 8 and ('|' in p[5] or p[5].startswith(('L','P', 'B', 'C'))):
                    try:
                        slides = int(p[6])
                    except:
                        slides = 1
                    try:
                        length = float(p[7])
                    except:
                        length = None
                    raw.append((x, y, t, slides, length) if length is not None else (x, y, t))
                else:
                    raw.append((x, y, t))
        return raw

    def build_hits_array(self, raw_objects):
        hits_array = []
        if raw_objects:
            base = raw_objects[0][2]
            for it in raw_objects:
                x, y, t = it[0], it[1], it[2]
                time_s = (t - base) / 1000.0
                if len(it) == 5:
                    slides, length = it[3], it[4]
                    dur = self.slider_duration_sec(length, slides, t, self.slider_mult, self.timing_points)
                    hits_array.append((x, y, time_s, dur))
                else:
                    hits_array.append((x, y, time_s))
        return hits_array

    def run(self):
        self.load_map()
        raw_objects = self.parse_hit_objects()
        self.hits_array = self.build_hits_array(raw_objects)
        print(self.hits_array)

        keyboard.wait("e")
        st = time.time()
        for timing in updated_offsets:
            while time.time() - st < timing:
                time.sleep(0.001)
                click()
                print(f"Pressed{timing}")

        for e in self.hits_array:
            temp = e[2]
            # 0x57 is W, 0x45 is E so change based on alternation
            key = 0x57 if self.alternated else 0x45
            self.alternated = not self.alternated
            if not self.tabbedin():
                print("Alt tabed. Stopping :)")
                break
            while time.time() - st < temp-0.001:
                pass
            if len(e) == 3:
                self.click_hold(0.001, key)
            else:
                self.click_hold(e[3], key)


if __name__ == "__main__":
    player = Relaxer()
    player.run()