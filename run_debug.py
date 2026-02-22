import traceback
import main
try:
    main.main()
except Exception as e:
    with open('err.txt', 'w') as f:
        f.write(traceback.format_exc())
